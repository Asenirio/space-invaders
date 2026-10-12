import pygame
import random
import math
from entities.player import Player, SHIP_COLOR_MAP
from entities.button import MobileButtons
from entities.enemy import Enemy
from entities.bullet import Bullet
from managers.db_manager import DBManager

SPACESHIPS = {
    "X-Wing": {
        "color_key": "yellow",
        "rgb": (255, 232, 31),
        "laser_color": (255, 50, 50),
        "speed": "Fast",
        "class": "Starfighter"
    },
    "TIE Fighter": {
        "color_key": "red",
        "rgb": (255, 30, 30),
        "laser_color": (50, 255, 50),
        "speed": "Very Fast",
        "class": "Interceptor"
    },
    "A-Wing": {
        "color_key": "cyan",
        "rgb": (0, 215, 255),
        "laser_color": (0, 215, 255),
        "speed": "Ultra Fast",
        "class": "Interceptor"
    },
    "Millennium Falcon": {
        "color_key": "violet",
        "rgb": (180, 0, 255),
        "laser_color": (255, 200, 0),
        "speed": "Medium",
        "class": "Freighter"
    },
    "Slave I": {
        "color_key": "purple",
        "rgb": (120, 0, 200),
        "laser_color": (255, 80, 0),
        "speed": "Balanced",
        "class": "Patrol Craft"
    }
}

SHIP_NAMES = list(SPACESHIPS.keys())
CONTROL_SCHEMES = ["arrows", "wasd"]
DIFFICULTIES    = ["easy", "normal", "hard"]
DIFFICULTY_LABELS = {"easy": "Padawan", "normal": "Jedi Knight", "hard": "Jedi Master"}

DIFFICULTY_SPAWN = {"easy": 3, "normal": 5, "hard": 8}

DARK_BG     = (3, 4, 10)
SW_YELLOW   = (255, 232, 31)
REBEL_BLUE  = (0, 162, 255)
SITH_RED    = (255, 35, 35)
WHITE       = (255, 255, 255)
GRAY        = (140, 145, 160)
DARK_BTN    = (18, 22, 32)
SEL_BTN     = (90, 70, 0)
GOLD        = (255, 215, 0)
PANEL_BG    = (12, 16, 24)
PANEL_BOR   = (45, 60, 85)
FIELD_BG    = (18, 24, 36)
RED_ERR     = (255, 80, 80)


class SpaceBattlefield:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.stars = [
            (random.randint(0, width), random.randint(0, height), random.choice([1, 1, 2]), random.randint(100, 255))
            for _ in range(160)
        ]
        self.bg_lasers = []
        self.explosions = []
        
        self.nebula_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        for _ in range(7):
            nx, ny = random.randint(0, width), random.randint(0, height)
            radius = random.randint(120, 250)
            color = random.choice([
                (20, 40, 90, 22),
                (80, 10, 40, 18),
                (40, 15, 70, 20),
            ])
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (radius, radius), radius)
            self.nebula_surf.blit(s, (nx - radius, ny - radius))

    def update_and_draw(self, screen):
        screen.fill(DARK_BG)
        screen.blit(self.nebula_surf, (0, 0))

        t = pygame.time.get_ticks()
        for x, y, r, brightness in self.stars:
            flicker = max(40, min(255, brightness + int(30 * math.sin(t * 0.005 + x))))
            pygame.draw.circle(screen, (flicker, flicker, flicker), (x, y), r)

        if random.random() < 0.05:
            start_x = random.randint(-100, self.width + 100)
            start_y = random.randint(0, self.height // 2)
            angle = random.uniform(0.2, 0.8)
            speed = random.randint(12, 22)
            color = random.choice([(255, 30, 30), (50, 255, 80)])
            self.bg_lasers.append({
                'x': start_x, 'y': start_y,
                'vx': speed * math.cos(angle), 'vy': speed * math.sin(angle),
                'color': color, 'length': random.randint(25, 45), 'life': 60
            })

        for laser in self.bg_lasers[:]:
            laser['x'] += laser['vx']
            laser['y'] += laser['vy']
            laser['life'] -= 1
            
            x1, y1 = laser['x'], laser['y']
            x2 = x1 - laser['vx'] * (laser['length'] / 10)
            y2 = y1 - laser['vy'] * (laser['length'] / 10)
            
            pygame.draw.line(screen, laser['color'], (x1, y1), (x2, y2), 2)

            if laser['life'] <= 0 or laser['x'] > self.width + 100 or laser['y'] > self.height + 100:
                if random.random() < 0.15:
                    self.explosions.append({
                        'x': laser['x'], 'y': laser['y'],
                        'radius': 2, 'max_radius': random.randint(15, 35),
                        'color': random.choice([(255, 180, 50), (255, 100, 30)])
                    })
                self.bg_lasers.remove(laser)

        for exp in self.explosions[:]:
            exp['radius'] += 1.5
            alpha = max(0, int(255 * (1 - (exp['radius'] / exp['max_radius']))))
            
            s = pygame.Surface((exp['radius'] * 2, exp['radius'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*exp['color'], alpha), (exp['radius'], exp['radius']), int(exp['radius']))
            screen.blit(s, (exp['x'] - exp['radius'], exp['y'] - exp['radius']))

            if exp['radius'] >= exp['max_radius']:
                self.explosions.remove(exp)


def draw_glass_panel(screen, rect, alpha=160, border_color=PANEL_BOR, border_radius=12):
    panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (12, 18, 30, alpha), panel_surf.get_rect(), border_radius=border_radius)
    screen.blit(panel_surf, rect.topleft)
    pygame.draw.rect(screen, border_color, rect, 1, border_radius=border_radius)


def draw_text_field(screen, font, rect, text, placeholder, focused, masked=False, visible=False, toggle_rect=None):
    border_color = SW_YELLOW if focused else PANEL_BOR
    bg_color     = (28, 34, 48) if focused else FIELD_BG

    pygame.draw.rect(screen, bg_color, rect, border_radius=8)
    pygame.draw.rect(screen, border_color, rect, 2 if focused else 1, border_radius=8)

    display = ("●" * len(text)) if masked and not visible else text
    surf = font.render(display if display else placeholder, True, WHITE if display else (100, 110, 130))

    text_x = rect.x + 14
    text_y = rect.y + (rect.height - surf.get_height()) // 2
    screen.blit(surf, (text_x, text_y))

    if masked and toggle_rect:
        draw_password_toggle(screen, toggle_rect, visible)


def draw_password_toggle(screen, rect, visible):
    pygame.draw.rect(screen, (24, 30, 44), rect, border_radius=6)
    pygame.draw.ellipse(screen, REBEL_BLUE if visible else (120, 130, 150),
                        pygame.Rect(rect.x + 8, rect.y + 10, rect.width - 16, rect.height - 20), 2)
    pygame.draw.circle(screen, REBEL_BLUE if visible else (120, 130, 150), rect.center, 4)


def draw_button(screen, font, rect, text, primary=True):
    if primary:
        pygame.draw.rect(screen, (50, 40, 0), rect, border_radius=8)
        pygame.draw.rect(screen, SW_YELLOW, rect, 2, border_radius=8)
        txt_color = SW_YELLOW
    else:
        pygame.draw.rect(screen, DARK_BTN, rect, border_radius=8)
        pygame.draw.rect(screen, PANEL_BOR, rect, 1, border_radius=8)
        txt_color = WHITE

    txt_surf = font.render(text, True, txt_color)
    screen.blit(txt_surf, (rect.centerx - txt_surf.get_width()  // 2,
                            rect.centery - txt_surf.get_height() // 2))


def draw_divider(screen, cx, y, width=340, color=None):
    if color is None:
        color = PANEL_BOR
    pygame.draw.line(screen, color, (cx - width // 2, y), (cx + width // 2, y), 2)


def draw_glow_title(screen, big_font, text, cx, y, color=SW_YELLOW):
    surf = big_font.render(text, True, color)
    screen.blit(surf, (cx - surf.get_width() // 2, y))


def clean_username(username):
    if not username:
        return "Guest"
    cleaned = "".join(c for c in username if c.isprintable() and ord(c) >= 32)
    return cleaned.strip() or "Guest"


def render_retro_score(score_val, color, scale=3):
    small_font = pygame.font.SysFont("Consolas", 14, bold=True)
    temp = small_font.render(str(score_val), False, color)
    w, h = temp.get_size()
    return pygame.transform.scale(temp, (int(w * scale), int(h * scale)))


class GameManager:
    def __init__(self, screen, screen_width, screen_height, player_name=""):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player_name = player_name
        self.db = DBManager(user="root", password="")
        self.leaderboard = []
        
        self.battlefield = SpaceBattlefield(screen_width, screen_height)

        self.font       = pygame.font.SysFont("Trebuchet MS", 26, bold=True)
        self.big_font   = pygame.font.SysFont("Impact", 58)
        self.small_font = pygame.font.SysFont("Trebuchet MS", 20)
        self.tiny_font  = pygame.font.SysFont("Trebuchet MS", 16)

        cx = screen_width // 2

        self.left_hero_panel  = pygame.Rect(40, 80, 310, 480)
        self.right_form_panel = pygame.Rect(370, 80, 430, 480)

        self.name_input_rect   = pygame.Rect(cx - 160, 320, 320, 52)
        self.start_button_rect = pygame.Rect(cx - 110, 400, 220, 52)
        self.profile_btn_rect  = pygame.Rect(cx - 110, 468, 220, 42)

        self.reload_button_rect = pygame.Rect(cx - 110, screen_height // 2 + 50, 220, 52)

        self.selected_ship        = "X-Wing"
        self.profile_ship_color   = SPACESHIPS["X-Wing"]["color_key"]
        self.profile_control      = "arrows"
        self.profile_difficulty   = "normal"
        
        self.profile_left_btn  = True
        self.profile_right_btn = True
        self.profile_fire_btn  = True

        self.profile_back_rect    = pygame.Rect(cx - 110, screen_height - 65, 220, 42)
        self.profile_option_rects = []

        rx = self.right_form_panel.centerx
        field_w = 340
        
        self.login_user_rect     = pygame.Rect(rx - field_w // 2, 210, field_w, 46)
        self.login_pass_rect     = pygame.Rect(rx - field_w // 2, 290, field_w, 46)
        self.login_pass_eye_rect = pygame.Rect(self.login_pass_rect.right - 42, self.login_pass_rect.y + 3, 38, 40)
        self.login_btn_rect      = pygame.Rect(rx - field_w // 2, 360, field_w, 48)
        self.login_lb_btn_rect   = pygame.Rect(rx - 100, 490, 200, 36)
        self.toggle_link_rect    = pygame.Rect(rx - 150, 425, 300, 24)

        self.reg_user_rect     = pygame.Rect(rx - field_w // 2, 185, field_w, 42)
        self.reg_pass_rect     = pygame.Rect(rx - field_w // 2, 255, field_w, 42)
        self.reg_conf_rect     = pygame.Rect(rx - field_w // 2, 325, field_w, 42)
        self.reg_pass_eye_rect = pygame.Rect(self.reg_pass_rect.right - 42, self.reg_pass_rect.y + 3, 38, 36)
        self.reg_conf_eye_rect = pygame.Rect(self.reg_conf_rect.right - 42, self.reg_conf_rect.y + 3, 38, 36)
        self.reg_create_rect   = pygame.Rect(rx - field_w // 2, 388, field_w, 46)

        self.lb_back_rect = pygame.Rect(cx - 100, 528, 200, 46)

        self.login_username  = ""
        self.login_password  = ""
        self.login_focus     = "username"
        self.login_error     = ""
        self.login_password_visible = False

        self.reg_username    = ""
        self.reg_password    = ""
        self.reg_confirm     = ""
        self.reg_focus       = "username"
        self.reg_error       = ""
        self.reg_success     = ""
        self.reg_password_visible = False
        self.reg_confirm_visible = False

        self.old_name = ""
        self.reset_game()

    def reset_game(self):
        self.player  = Player(self.screen_width, self.screen_height, self.profile_ship_color)
        self.buttons = MobileButtons(
            left_enabled=self.profile_left_btn,
            right_enabled=self.profile_right_btn,
            fire_enabled=self.profile_fire_btn
        )
        self.bullet  = None
        self.enemies = []

        self.score         = 0
        self.personal_best = 0
        self.spawn_number  = DIFFICULTY_SPAWN.get(self.profile_difficulty, 5)
        self.game_state    = "login"

        self.old_name       = self.player_name
        self.player_history = []
        self.timer          = 0
        self.state_timer    = 0

        self.login_username = self.player_name
        self.login_password = ""
        self.login_error    = ""

    def _load_profile_from_db(self):
        if not self.player_name:
            return
        profile = self.db.get_player_profile(self.player_name)
        if profile:
            ship_color_saved = profile.get("ship_color", "yellow") or "yellow"
            self.profile_control    = profile.get("control_scheme", "arrows") or "arrows"
            self.profile_difficulty = profile.get("difficulty", "normal") or "normal"
            self.profile_left_btn   = bool(profile.get("btn_left_enabled", 1))
            self.profile_right_btn  = bool(profile.get("btn_right_enabled", 1))
            self.profile_fire_btn   = bool(profile.get("btn_fire_enabled", 1))
            
            for name, data in SPACESHIPS.items():
                if data["color_key"] == ship_color_saved:
                    self.selected_ship = name
                    self.profile_ship_color = ship_color_saved
                    break
            self.player.set_color(self.profile_ship_color)
        self.personal_best = self.db.get_player_best_score(self.player_name)

    def _save_profile_to_db(self):
        if not self.player_name:
            return
        self.db.get_or_create_player(self.player_name)
        self.db.update_player_profile(
            self.player_name,
            ship_color     = self.profile_ship_color,
            control_scheme = self.profile_control,
            difficulty     = self.profile_difficulty,
            left_en        = self.profile_left_btn,
            right_en       = self.profile_right_btn,
            fire_en        = self.profile_fire_btn
        )

    def _after_login(self):
        self._load_profile_from_db()
        self.spawn_number = DIFFICULTY_SPAWN.get(self.profile_difficulty, 5)
        self.player.set_color(self.profile_ship_color)
        self.game_state = "name_input"

    def _start_game(self):
        self.player_name = self.player_name.strip() or "Guest"
        if self.old_name and self.old_name != self.player_name:
            self.db.update_player_username(self.old_name, self.player_name)
        self.db.get_or_create_player(self.player_name)
        self._load_profile_from_db()
        self.spawn_number = DIFFICULTY_SPAWN.get(self.profile_difficulty, 5)
        self.player.set_color(self.profile_ship_color)
        self.buttons = MobileButtons(
            left_enabled=self.profile_left_btn,
            right_enabled=self.profile_right_btn,
            fire_enabled=self.profile_fire_btn
        )
        self.game_state = "playing"
        self.spawn_enemies()

    def _handle_text_input(self, event, field_name, max_len=50):
        current = getattr(self, field_name)
        ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
        selected = getattr(self, f"_{field_name}_select_all", False)
        if event.key == pygame.K_a and ctrl:
            setattr(self, f"_{field_name}_select_all", True)
        elif event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
            current = "" if (ctrl or selected) else current[:-1]
            setattr(self, f"_{field_name}_select_all", False)
        elif event.unicode and event.unicode.isprintable() and event.key != pygame.K_TAB:
            if selected:
                current = ""
            if len(current) < max_len:
                current += event.unicode
            setattr(self, f"_{field_name}_select_all", False)
        setattr(self, field_name, current)

    def spawn_enemies(self):
        self.enemies = []
        for i in range(self.spawn_number):
            self.enemies.append(Enemy(i, self.spawn_number, self.screen_width, self.screen_height))
        self.timer = 0

    def update(self, events):
        if self.game_state == "login":
            self._update_login(events)
        elif self.game_state == "register":
            self._update_register(events)
        elif self.game_state == "leaderboard":
            self._update_leaderboard(events)
        elif self.game_state == "name_input":
            self._update_name_input(events)
        elif self.game_state == "profile":
            self._update_profile(events)
        elif self.game_state in ("playing", "blinking"):
            self._update_playing(events)
        elif self.game_state == "game_over":
            self._update_game_over(events)

    def _draw_dual_column_layout(self, form_title):
        draw_glass_panel(self.screen, self.left_hero_panel, alpha=180, border_color=PANEL_BOR)
        
        lx = self.left_hero_panel.centerx
        title = self.big_font.render("INVADER", True, SW_YELLOW)
        subtitle = self.tiny_font.render("GALACTIC ALLIANCE HQ", True, REBEL_BLUE)
        self.screen.blit(title, (lx - title.get_width() // 2, 105))
        self.screen.blit(subtitle, (lx - subtitle.get_width() // 2, 155))

        pygame.draw.line(self.screen, PANEL_BOR, (self.left_hero_panel.x + 20, 185), (self.left_hero_panel.right - 20, 185), 1)

        stats = [
            ("DEFENSE GRID", "ACTIVE", (50, 220, 100)),
            ("HOLONET LINK", "ONLINE", (50, 220, 100)),
            ("ACTIVE SECTOR", "OUTER RIM", SW_YELLOW),
            ("FLEET READINESS", "100%", REBEL_BLUE),
        ]
        
        sy = 205
        for label, val, col in stats:
            lbl_surf = self.tiny_font.render(label, True, GRAY)
            val_surf = self.small_font.render(val, True, col)
            self.screen.blit(lbl_surf, (self.left_hero_panel.x + 24, sy))
            self.screen.blit(val_surf, (self.left_hero_panel.right - 24 - val_surf.get_width(), sy - 2))
            sy += 42

        pygame.draw.line(self.screen, PANEL_BOR, (self.left_hero_panel.x + 20, sy + 5), (self.left_hero_panel.right - 20, sy + 5), 1)
        
        fleet_lbl = self.tiny_font.render("COMMAND ACCESS STATUS", True, SW_YELLOW)
        self.screen.blit(fleet_lbl, (lx - fleet_lbl.get_width() // 2, sy + 20))
        
        status_box = pygame.Rect(self.left_hero_panel.x + 24, sy + 45, self.left_hero_panel.width - 48, 50)
        pygame.draw.rect(self.screen, (18, 26, 40), status_box, border_radius=8)
        pygame.draw.rect(self.screen, REBEL_BLUE, status_box, 1, border_radius=8)
        
        st_txt = self.tiny_font.render("AWAITING CREDENTIALS...", True, WHITE)
        self.screen.blit(st_txt, (status_box.centerx - st_txt.get_width() // 2, status_box.centery - st_txt.get_height() // 2))

        draw_glass_panel(self.screen, self.right_form_panel, alpha=200, border_color=PANEL_BOR)
        
        rx = self.right_form_panel.centerx
        f_title = self.font.render(form_title, True, SW_YELLOW)
        self.screen.blit(f_title, (rx - f_title.get_width() // 2, 105))
        pygame.draw.line(self.screen, PANEL_BOR, (self.right_form_panel.x + 20, 142), (self.right_form_panel.right - 20, 142), 1)

    def _update_login(self, events):
        rx = self.right_form_panel.centerx

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.login_focus = "password" if self.login_focus == "username" else "username"
                elif event.key == pygame.K_RETURN:
                    self._do_login()
                    return
                elif self.login_focus == "username":
                    self._handle_text_input(event, "login_username")
                elif self.login_focus == "password":
                    self._handle_text_input(event, "login_password")

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.toggle_link_rect.collidepoint(event.pos):
                    self.reg_username = self.login_username
                    self.game_state = "register"
                    return
                elif self.login_pass_eye_rect.collidepoint(event.pos):
                    self.login_password_visible = not self.login_password_visible
                elif self.login_user_rect.collidepoint(event.pos):
                    self.login_focus = "username"
                elif self.login_pass_rect.collidepoint(event.pos):
                    self.login_focus = "password"
                elif self.login_btn_rect.collidepoint(event.pos):
                    self._do_login()
                    return
                elif self.login_lb_btn_rect.collidepoint(event.pos):
                    self.leaderboard = self.db.get_top_scores(limit=10)
                    self.game_state  = "leaderboard"
                    return

        self.battlefield.update_and_draw(self.screen)
        self._draw_dual_column_layout("PILOT AUTHENTICATION")

        lbl_u = self.tiny_font.render("CALLSIGN", True, REBEL_BLUE)
        lbl_p = self.tiny_font.render("ACCESS CODE", True, REBEL_BLUE)
        self.screen.blit(lbl_u, (self.login_user_rect.x + 2, self.login_user_rect.y - 20))
        self.screen.blit(lbl_p, (self.login_pass_rect.x + 2, self.login_pass_rect.y - 20))

        draw_text_field(self.screen, self.font, self.login_user_rect,
                        self.login_username, "Enter Callsign...", self.login_focus == "username")
        draw_text_field(self.screen, self.font, self.login_pass_rect,
                        self.login_password, "Enter Access Code...", self.login_focus == "password",
                        masked=True, visible=self.login_password_visible, toggle_rect=self.login_pass_eye_rect)

        draw_button(self.screen, self.font, self.login_btn_rect, "AUTHENTICATE", primary=True)

        toggle_txt = self.tiny_font.render("Need an account? Enlist Pilot", True, REBEL_BLUE)
        self.screen.blit(toggle_txt, (rx - toggle_txt.get_width() // 2, self.toggle_link_rect.y))

        draw_divider(self.screen, rx, 470, width=320, color=PANEL_BOR)
        draw_button(self.screen, self.small_font, self.login_lb_btn_rect, "Leaderboard", primary=False)

        if self.login_error:
            err_bg = pygame.Rect(rx - 160, 338, 320, 20)
            pygame.draw.rect(self.screen, (50, 10, 10), err_bg, border_radius=4)
            err = self.tiny_font.render(self.login_error, True, RED_ERR)
            self.screen.blit(err, (rx - err.get_width() // 2, 340))

    def _do_login(self):
        if not self.login_username.strip():
            self.login_error = "Please enter a username."
            return
        if not self.login_password:
            self.login_error = "Please enter a password."
            return

        player_row = self.db.login_player(self.login_username.strip(), self.login_password)
        if player_row:
            self.player_name    = player_row["username"]
            self.login_error    = ""
            self.login_password = ""
            self._after_login()
        else:
            self.login_error = "Incorrect username or password."

    def _update_register(self, events):
        rx = self.right_form_panel.centerx

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._do_register()
                    return
                elif self.reg_focus == "username":
                    self._handle_text_input(event, "reg_username")
                elif self.reg_focus == "password":
                    self._handle_text_input(event, "reg_password")
                elif self.reg_focus == "confirm":
                    self._handle_text_input(event, "reg_confirm")

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.toggle_link_rect.collidepoint(event.pos):
                    self.login_username = self.reg_username
                    self.game_state = "login"
                    return
                elif self.reg_pass_eye_rect.collidepoint(event.pos):
                    self.reg_password_visible = not self.reg_password_visible
                elif self.reg_conf_eye_rect.collidepoint(event.pos):
                    self.reg_confirm_visible = not self.reg_confirm_visible
                elif self.reg_user_rect.collidepoint(event.pos):
                    self.reg_focus = "username"
                elif self.reg_pass_rect.collidepoint(event.pos):
                    self.reg_focus = "password"
                elif self.reg_conf_rect.collidepoint(event.pos):
                    self.reg_focus = "confirm"
                elif self.reg_create_rect.collidepoint(event.pos):
                    self._do_register()
                    return

        self.battlefield.update_and_draw(self.screen)
        self._draw_dual_column_layout("RECRUIT ENLISTMENT")

        labels_data = [
            ("CALLSIGN (MIN 3 CHARS)",      self.reg_user_rect),
            ("ACCESS CODE (MIN 4 CHARS)",  self.reg_pass_rect),
            ("CONFIRM ACCESS CODE",        self.reg_conf_rect),
        ]
        for lbl_text, f_rect in labels_data:
            lbl = self.tiny_font.render(lbl_text, True, REBEL_BLUE)
            self.screen.blit(lbl, (f_rect.x + 2, f_rect.y - 18))

        draw_text_field(self.screen, self.font, self.reg_user_rect, self.reg_username, "Desired Callsign...", self.reg_focus == "username")
        draw_text_field(self.screen, self.font, self.reg_pass_rect, self.reg_password, "Access Code...", self.reg_focus == "password", masked=True, visible=self.reg_password_visible, toggle_rect=self.reg_pass_eye_rect)
        draw_text_field(self.screen, self.font, self.reg_conf_rect, self.reg_confirm,  "Re-enter Code...", self.reg_focus == "confirm", masked=True, visible=self.reg_confirm_visible, toggle_rect=self.reg_conf_eye_rect)

        draw_button(self.screen, self.font, self.reg_create_rect, "CREATE ACCOUNT", primary=True)

        toggle_txt = self.tiny_font.render("Already registered? Sign In", True, REBEL_BLUE)
        self.screen.blit(toggle_txt, (rx - toggle_txt.get_width() // 2, 448))

        if self.reg_error:
            err_bg = pygame.Rect(rx - 160, 480, 320, 22)
            pygame.draw.rect(self.screen, (50, 10, 10), err_bg, border_radius=4)
            err = self.tiny_font.render(self.reg_error, True, RED_ERR)
            self.screen.blit(err, (rx - err.get_width() // 2, 482))

    def _do_register(self):
        username = self.reg_username.strip()
        password = self.reg_password
        confirm  = self.reg_confirm

        if not username or len(username) < 3:
            self.reg_error = "Callsign must be at least 3 characters."
            return
        if not password or len(password) < 4:
            self.reg_error = "Access Code must be at least 4 characters."
            return
        if password != confirm:
            self.reg_error = "Access Codes do not match."
            return

        ok, result = self.db.register_player(username, password)
        if ok:
            self.player_name = username
            self.reg_error   = ""
            self._after_login()
        else:
            self.reg_error = result

    def _update_leaderboard(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.lb_back_rect.collidepoint(event.pos):
                    self.game_state = "login"
                    return
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.game_state = "login"
                return

        self.battlefield.update_and_draw(self.screen)

        cx = self.screen_width // 2
        draw_glow_title(self.screen, self.big_font, "LEADERBOARD", cx, 18, color=SW_YELLOW)

        sub = self.small_font.render("Top Galactic Aces", True, REBEL_BLUE)
        self.screen.blit(sub, (cx - sub.get_width() // 2, 90))

        draw_divider(self.screen, cx, 118, width=320, color=SW_YELLOW)

        table_rect = pygame.Rect(cx - 285, 126, 570, 384)
        draw_glass_panel(self.screen, table_rect, alpha=220)

        header_y = 138
        rank_x, name_x, score_center_x, date_x = cx - 258, cx - 190, cx + 125, cx + 172

        for h_text, h_x in [("#", rank_x), ("PILOT", name_x), ("DATE", date_x)]:
            h_surf = self.tiny_font.render(h_text, True, SW_YELLOW)
            self.screen.blit(h_surf, (h_x, header_y))

        score_lbl_surf = self.tiny_font.render("SCORE", True, SW_YELLOW)
        self.screen.blit(score_lbl_surf, (score_center_x - score_lbl_surf.get_width() // 2, header_y))

        pygame.draw.line(self.screen, PANEL_BOR, (table_rect.x + 12, header_y + 24), (table_rect.right - 12, header_y + 24), 1)

        if not self.leaderboard:
            no_data = self.font.render("No HoloNet scores recorded yet!", True, GRAY)
            self.screen.blit(no_data, (cx - no_data.get_width() // 2, 285))
        else:
            row_y = header_y + 32
            rank_colors = {1: GOLD, 2: (210, 210, 210), 3: (205, 130, 55)}
            for i, entry in enumerate(self.leaderboard, start=1):
                display_name = clean_username(entry["username"])
                is_me     = (entry["username"] == self.player_name)
                row_color = SW_YELLOW if is_me else (220, 220, 230)

                rank_surf  = self.small_font.render(str(i), True, rank_colors.get(i, (120, 130, 150)))
                name_surf  = self.small_font.render(display_name[:18], True, row_color)
                score_surf = self.font.render(str(entry["score"]), True, row_color)

                date_str  = str(entry.get("achieved_at"))[:10] if entry.get("achieved_at") else "—"
                date_surf = self.tiny_font.render(date_str, True, (110, 120, 140))

                self.screen.blit(rank_surf,  (rank_x,  row_y))
                self.screen.blit(name_surf,  (name_x,  row_y))
                self.screen.blit(score_surf, (score_center_x - score_surf.get_width() // 2, row_y - 2))
                self.screen.blit(date_surf,  (date_x,  row_y + 6))
                row_y += 34

        draw_button(self.screen, self.font, self.lb_back_rect, "< BACK", primary=False)

    def _update_name_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_RETURN:
                    self._start_game()
                    return
                elif event.unicode.isprintable() and len(self.player_name) < 15:
                    self.player_name += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.start_button_rect.collidepoint(event.pos):
                    self._start_game()
                    return
                if self.profile_btn_rect.collidepoint(event.pos):
                    self.player_name = self.player_name.strip() or "Guest"
                    self.db.get_or_create_player(self.player_name)
                    self._load_profile_from_db()
                    self.game_state = "profile"
                    return

        self.battlefield.update_and_draw(self.screen)

        cx = self.screen_width // 2
        draw_glow_title(self.screen, self.big_font, "INVADERS", cx, 48, color=SW_YELLOW)

        draw_divider(self.screen, cx, 126, width=280, color=PANEL_BOR)

        card = pygame.Rect(cx - 210, 142, 420, 96)
        draw_glass_panel(self.screen, card, alpha=200)

        pilot_lbl = self.tiny_font.render("PILOT CALLSIGN", True, SW_YELLOW)
        pilot_val = self.font.render(self.player_name, True, REBEL_BLUE)
        self.screen.blit(pilot_lbl, (cx - 180, card.y + 22))
        self.screen.blit(pilot_val, (cx - 180, card.y + 44))

        pygame.draw.line(self.screen, PANEL_BOR, (cx, card.y + 16), (cx, card.bottom - 16), 1)

        pb_rect = pygame.Rect(cx + 20, card.y + 18, 160, 60)
        pygame.draw.rect(self.screen, (35, 28, 5), pb_rect, border_radius=8)
        pygame.draw.rect(self.screen, SW_YELLOW, pb_rect, 1, border_radius=8)

        pb_lbl = self.tiny_font.render("HIGH SCORE", True, SW_YELLOW)
        pb_val = render_retro_score(self.personal_best, GOLD, scale=1.8)
        self.screen.blit(pb_lbl, (pb_rect.centerx - pb_lbl.get_width() // 2, pb_rect.y + 8))
        self.screen.blit(pb_val, (pb_rect.centerx - pb_val.get_width() // 2, pb_rect.y + 26))

        draw_text_field(self.screen, self.font, self.name_input_rect, self.player_name, "Your callsign...", True)

        draw_button(self.screen, self.font, self.start_button_rect, "LAUNCH MISSION", primary=True)
        draw_button(self.screen, self.small_font, self.profile_btn_rect, "SHIP CUSTOMIZATION", primary=False)

    def _update_profile(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, category, value in self.profile_option_rects:
                    if rect.collidepoint(event.pos):
                        if category == "ship":
                            self.selected_ship = value
                            self.profile_ship_color = SPACESHIPS[value]["color_key"]
                            self.player.set_color(self.profile_ship_color)
                        elif category == "control":
                            self.profile_control = value
                        elif category == "difficulty":
                            self.profile_difficulty = value
                        elif category == "toggle_left":
                            self.profile_left_btn = not self.profile_left_btn
                        elif category == "toggle_right":
                            self.profile_right_btn = not self.profile_right_btn
                        elif category == "toggle_fire":
                            self.profile_fire_btn = not self.profile_fire_btn

                if self.profile_back_rect.collidepoint(event.pos):
                    self._save_profile_to_db()
                    self.game_state = "name_input"

        self.battlefield.update_and_draw(self.screen)
        self.profile_option_rects = []

        cx = self.screen_width // 2
        draw_glow_title(self.screen, self.big_font, "SHIP HANGAR", cx, 15, color=SW_YELLOW)
        draw_divider(self.screen, cx, 80, width=280, color=PANEL_BOR)

        ship_info = SPACESHIPS[self.selected_ship]

        preview_card = pygame.Rect(cx - 240, 92, 480, 85)
        draw_glass_panel(self.screen, preview_card, alpha=200)
        
        sprite_box = pygame.Rect(cx - 230, 99, 70, 70)
        pygame.draw.rect(self.screen, FIELD_BG, sprite_box, border_radius=8)
        pygame.draw.rect(self.screen, ship_info["rgb"], sprite_box, 2, border_radius=8)
        self.screen.blit(self.player.image, (cx - 225, 104))

        title_s = self.font.render(self.selected_ship, True, SW_YELLOW)
        class_s = self.tiny_font.render(f"Class: {ship_info['class']}", True, REBEL_BLUE)
        speed_s = self.tiny_font.render(f"Speed: {ship_info['speed']}", True, WHITE)
        self.screen.blit(title_s, (cx - 145, 98))
        self.screen.blit(class_s, (cx - 145, 126))
        self.screen.blit(speed_s, (cx - 145, 146))

        y_pos = 188
        grid_title = self.tiny_font.render("SELECT SPACESHIP:", True, WHITE)
        self.screen.blit(grid_title, (cx - 240, y_pos))
        
        y_pos += 22
        card_w, card_h = 90, 44
        gap = 8
        start_x = cx - 240

        for i, name in enumerate(SHIP_NAMES):
            s_data = SPACESHIPS[name]
            bx = start_x + (i * (card_w + gap))
            btn_rect = pygame.Rect(bx, y_pos, card_w, card_h)
            
            is_sel = (name == self.selected_ship)
            bg_col = SEL_BTN if is_sel else DARK_BTN
            bor_col = SW_YELLOW if is_sel else PANEL_BOR

            pygame.draw.rect(self.screen, bg_col, btn_rect, border_radius=6)
            pygame.draw.rect(self.screen, bor_col, btn_rect, 2 if is_sel else 1, border_radius=6)

            short_name = name.split()[-1] if len(name) > 10 else name
            txt = self.tiny_font.render(short_name, True, SW_YELLOW if is_sel else WHITE)
            self.screen.blit(txt, (btn_rect.centerx - txt.get_width() // 2, btn_rect.centery - txt.get_height() // 2))

            self.profile_option_rects.append((btn_rect, "ship", name))

        y_pos += 56
        ctrl_lbl = self.tiny_font.render("Controls:", True, WHITE)
        self.screen.blit(ctrl_lbl, (cx - 240, y_pos + 6))
        
        c_x = cx - 120
        for scheme in CONTROL_SCHEMES:
            c_rect = pygame.Rect(c_x, y_pos, 110, 34)
            is_sel = (scheme == self.profile_control)
            pygame.draw.rect(self.screen, SEL_BTN if is_sel else DARK_BTN, c_rect, border_radius=6)
            pygame.draw.rect(self.screen, SW_YELLOW if is_sel else PANEL_BOR, c_rect, 2 if is_sel else 1, border_radius=6)

            c_txt = self.tiny_font.render(scheme.upper(), True, WHITE)
            self.screen.blit(c_txt, (c_rect.centerx - c_txt.get_width() // 2, c_rect.centery - c_txt.get_height() // 2))
            
            self.profile_option_rects.append((c_rect, "control", scheme))
            c_x += 120

        y_pos += 48
        mob_lbl = self.tiny_font.render("Mobile Buttons (On/Off Hiding):", True, SW_YELLOW)
        self.screen.blit(mob_lbl, (cx - 240, y_pos))

        y_pos += 26
        toggles_info = [
            ("Left Btn", self.profile_left_btn, "toggle_left", cx - 240),
            ("Right Btn", self.profile_right_btn, "toggle_right", cx - 80),
            ("Fire Btn", self.profile_fire_btn, "toggle_fire", cx + 80),
        ]

        for label, state, action_key, tx in toggles_info:
            t_rect = pygame.Rect(tx, y_pos, 150, 36)
            bg_col = (40, 80, 40) if state else (80, 30, 30)
            bor_col = (50, 255, 50) if state else (255, 50, 50)

            pygame.draw.rect(self.screen, bg_col, t_rect, border_radius=6)
            pygame.draw.rect(self.screen, bor_col, t_rect, 2, border_radius=6)

            status_text = f"{label}: ON" if state else f"{label}: OFF"
            t_txt = self.tiny_font.render(status_text, True, WHITE)
            self.screen.blit(t_txt, (t_rect.centerx - t_txt.get_width() // 2, t_rect.centery - t_txt.get_height() // 2))

            self.profile_option_rects.append((t_rect, action_key, None))

        draw_button(self.screen, self.font, self.profile_back_rect, "SAVE & BACK", primary=True)

    def _update_playing(self, events):
        if self.game_state in ("playing", "blinking"):
            self.player_history.append((self.player.x, self.player.y))
            if len(self.player_history) > 60:
                self.player_history.pop(0)

        if self.game_state == "playing":
            keys = pygame.key.get_pressed()
            use_wasd = (self.profile_control == "wasd")

            left_key  = pygame.K_a if use_wasd else pygame.K_LEFT
            right_key = pygame.K_d if use_wasd else pygame.K_RIGHT

            if keys[left_key]:
                self.player.move_left()
            if keys[right_key]:
                self.player.move_right()

            screen_button_fired = self.buttons.handle_mouse(self.player, events)
            keyboard_fired = any(e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE for e in events)

            if (screen_button_fired or keyboard_fired) and self.bullet is None:
                bullet_x = self.player.x + self.player.width // 2 - 16
                self.bullet = Bullet(bullet_x, self.player.y)

            self.player.keep_inside_screen()

            if self.bullet:
                self.bullet.update()
                if not self.bullet.is_active:
                    self.bullet = None

            self.timer += 1
            if self.timer >= 180:
                waiting = [e for e in self.enemies if e.state == "waiting"]
                if waiting:
                    chosen = random.choice(waiting)
                    tx, ty = self.player_history[-1] if self.player_history else (self.player.x, self.player.y)
                    chosen.start_drop(tx, ty)
                    self.timer = 0

            all_despawned = all(e.state == "offscreen" for e in self.enemies)
            for enemy in self.enemies:
                enemy.update()

            if all_despawned:
                self.spawn_number += 1
                self.spawn_enemies()

            self.check_collisions()

        elif self.game_state == "blinking":
            self.player.update_blink()
            self.state_timer += 1
            for enemy in self.enemies:
                enemy.update()

            if self.state_timer >= 180:
                self.db.save_score(self.player_name, self.score)
                if self.score > self.personal_best:
                    self.personal_best = self.score
                self.leaderboard = self.db.get_top_scores(limit=10)
                self.game_state = "game_over"

        self.battlefield.update_and_draw(self.screen)

        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        if self.bullet:
            self.bullet.draw(self.screen)
        self.buttons.draw(self.screen)

        score_bg = pygame.Rect(10, 10, 150, 38)
        pygame.draw.rect(self.screen, PANEL_BG, score_bg, border_radius=6)
        pygame.draw.rect(self.screen, PANEL_BOR, score_bg, 1, border_radius=6)
        score_lbl = self.tiny_font.render("SCORE", True, SW_YELLOW)
        self.screen.blit(score_lbl, (18, 20))
        
        score_val = render_retro_score(self.score, WHITE, scale=1.8)
        self.screen.blit(score_val, (84, 17))

        pb_bg = pygame.Rect(10, 54, 150, 38)
        pygame.draw.rect(self.screen, PANEL_BG, pb_bg, border_radius=6)
        pygame.draw.rect(self.screen, PANEL_BOR, pb_bg, 1, border_radius=6)
        pb_lbl = self.tiny_font.render("BEST", True, SW_YELLOW)
        self.screen.blit(pb_lbl, (18, 64))
        
        pb_val = render_retro_score(self.personal_best, GOLD, scale=1.8)
        self.screen.blit(pb_val, (84, 61))

    def _update_game_over(self, events):
        cx = self.screen_width // 2

        self.reload_button_rect = pygame.Rect(cx - 100, 360, 200, 50)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.reload_button_rect.collidepoint(event.pos):
                    saved_name   = self.player_name
                    saved_best   = self.personal_best
                    saved_color  = self.profile_ship_color
                    saved_ctrl   = self.profile_control
                    saved_diff   = self.profile_difficulty
                    saved_ship   = self.selected_ship
                    self.reset_game()
                    self.player_name        = saved_name
                    self.personal_best      = saved_best
                    self.profile_ship_color = saved_color
                    self.profile_control    = saved_ctrl
                    self.profile_difficulty = saved_diff
                    self.selected_ship      = saved_ship
                    self.player.set_color(saved_color)
                    self.spawn_number = DIFFICULTY_SPAWN.get(saved_diff, 5)
                    self.game_state   = "name_input"
                    return

        self.battlefield.update_and_draw(self.screen)

        draw_glow_title(self.screen, self.big_font, "DEFEAT IN SPACE", cx, 80, color=SITH_RED)

        score_card = pygame.Rect(cx - 160, 180, 320, 110)
        draw_glass_panel(self.screen, score_card, alpha=200)

        sc_lbl = self.tiny_font.render("FINAL SCORE", True, SW_YELLOW)
        self.screen.blit(sc_lbl, (cx - sc_lbl.get_width() // 2, 195))
        
        sc_val = render_retro_score(self.score, WHITE, scale=3.6)
        self.screen.blit(sc_val, (cx - sc_val.get_width() // 2, 225))

        draw_button(self.screen, self.font, self.reload_button_rect, "RETRY MISSION", primary=True)

    def check_collisions(self):
        player_rect = self.player.get_rect()

        for enemy in self.enemies:
            if enemy.state == "offscreen":
                continue

            enemy_rect = enemy.get_rect()

            if player_rect.colliderect(enemy_rect):
                self.game_state         = "blinking"
                self.player.is_blinking = True
                self.state_timer        = 0
                return

            if self.bullet and self.bullet.get_rect().colliderect(enemy_rect):
                enemy.state  = "offscreen"
                self.bullet  = None
                self.score  += 1
                break