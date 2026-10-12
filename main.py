import pygame
from managers.game_manager import GameManager

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders by: Aseniero, Mario Jr. L.")

try:
    pygame.scrap.init()
except Exception:
    pass

game_manager = GameManager(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

clock = pygame.time.Clock()
running = True

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    game_manager.update(events)

    pygame.display.update()
    clock.tick(60)

pygame.quit()