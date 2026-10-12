import pygame
import os

class Bullet:
    def __init__(self, x, y):
        self.width = 32
        self.height = 32

        img_path = os.path.join("assets", "bullet.png")
        if os.path.exists(img_path):
            self.image = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        else:
            self.image = self._create_fallback_bullet()

        self.x = x
        self.y = y
        self.speed = 7
        self.is_active = True

    def _create_fallback_bullet(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 225, 255), (self.width // 2 - 3, 0, 6, self.height), border_radius=3)
        return surf

    def update(self):
        self.y -= self.speed
        if self.y < -self.height:
            self.is_active = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.is_active:
            screen.blit(self.image, (self.x, self.y))