import pygame
import os

SHIP_COLOR_MAP = {
    "violet": (190, 0,   255),
    "cyan":   (0,   220, 255),
    "red":    (255, 60,  60),
    "yellow": (255, 230, 0),
    "purple": (130, 0,   255),
}

class Player:
    def __init__(self, screen_width, screen_height, ship_color="violet"):
        self.width = 80
        self.height = 80
        self.speed = 5

        img_path = os.path.join("assets", "myship.png")
        if os.path.exists(img_path):
            raw = pygame.image.load(img_path).convert_alpha()
            self.base_image = pygame.transform.scale(raw, (self.width, self.height))
            self.gray_image = self._make_grayscale(self.base_image)
        else:
            # Fallback procedurally generated shape if image asset is missing
            self.base_image = self._create_fallback_ship()
            self.gray_image = self.base_image.copy()

        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - 100
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.is_blinking = False
        self.blink_timer = 0
        self.visible = True

        self.set_color(ship_color)

    def _create_fallback_ship(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        points = [
            (self.width // 2, 0),
            (self.width, self.height),
            (self.width // 2, self.height - 15),
            (0, self.height)
        ]
        pygame.draw.polygon(surf, (200, 200, 200), points)
        return surf

    @staticmethod
    def _make_grayscale(surface):
        w, h = surface.get_size()
        gray = pygame.Surface((w, h), flags=pygame.SRCALPHA)
        for px in range(w):
            for py in range(h):
                r, g, b, a = surface.get_at((px, py))
                lum = int(0.299 * r + 0.587 * g + 0.114 * b)
                lum = min(255, int(lum * 1.9))
                gray.set_at((px, py), (lum, lum, lum, a))
        return gray

    def set_color(self, color_name):
        tint = SHIP_COLOR_MAP.get(color_name, SHIP_COLOR_MAP["violet"])
        self.image = self.gray_image.copy()

        w, h = self.image.get_size()
        tint_surf = pygame.Surface((w, h), flags=pygame.SRCALPHA)
        tint_surf.fill((tint[0], tint[1], tint[2], 255))

        self.image.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    def move_left(self):
        if not self.is_blinking:
            self.x -= self.speed

    def move_right(self):
        if not self.is_blinking:
            self.x += self.speed

    def keep_inside_screen(self):
        self.x = max(0, min(self.x, self.screen_width - self.width))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update_blink(self):
        if self.is_blinking:
            self.blink_timer += 1
            if self.blink_timer % 10 == 0:
                self.visible = not self.visible
        else:
            self.visible = True

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, (self.x, self.y))