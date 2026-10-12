import pygame

class MobileButtons:
    def __init__(self, left_enabled=True, right_enabled=True, fire_enabled=True):
        self.left = pygame.Rect(20, 520, 80, 60)
        self.right = pygame.Rect(120, 520, 80, 60)
        self.fire = pygame.Rect(660, 515, 120, 70)
        
        self.left_enabled = left_enabled
        self.right_enabled = right_enabled
        self.fire_enabled = fire_enabled

    def draw(self, screen):
        btn_bg = (24, 12, 45)
        border_violet = (189, 0, 255)
        fire_violet = (220, 30, 110)

        # Draw Left Button only if enabled
        if self.left_enabled:
            pygame.draw.rect(screen, btn_bg, self.left, border_radius=12)
            pygame.draw.rect(screen, border_violet, self.left, 2, border_radius=12)
            pygame.draw.polygon(screen, border_violet, [(self.left.centerx + 8, self.left.centery - 12),
                                                        (self.left.centerx - 10, self.left.centery),
                                                        (self.left.centerx + 8, self.left.centery + 12)])

        # Draw Right Button only if enabled
        if self.right_enabled:
            pygame.draw.rect(screen, btn_bg, self.right, border_radius=12)
            pygame.draw.rect(screen, border_violet, self.right, 2, border_radius=12)
            pygame.draw.polygon(screen, border_violet, [(self.right.centerx - 8, self.right.centery - 12),
                                                        (self.right.centerx + 10, self.right.centery),
                                                        (self.right.centerx - 8, self.right.centery + 12)])

        # Draw Fire Button only if enabled
        if self.fire_enabled:
            pygame.draw.rect(screen, (60, 10, 35), self.fire, border_radius=14)
            pygame.draw.rect(screen, fire_violet, self.fire, 2, border_radius=14)
            font = pygame.font.SysFont("Arial", 18, bold=True)
            txt = font.render("FIRE", True, (255, 255, 255))
            screen.blit(txt, (self.fire.centerx - txt.get_width() // 2, self.fire.centery - txt.get_height() // 2))

    def handle_mouse(self, player, events):
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:
            mouse_pos = pygame.mouse.get_pos()
            if self.left_enabled and self.left.collidepoint(mouse_pos):
                player.move_left()
            if self.right_enabled and self.right.collidepoint(mouse_pos):
                player.move_right()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.fire_enabled and self.fire.collidepoint(event.pos):
                    return True
        return False