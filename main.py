import pygame
import sys
from game import SnakeGame
from constants import WIDTH, HEIGHT, GRID_SIZE  # Importiere Konstanten für Konsistenz

# Initialisiere Pygame
pygame.init()

# Erstelle das Fenster mit Konstanten aus constants.py
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake AI")

# Erstelle das Spiel ohne Parameterübergabe
game = SnakeGame()

# Spielschleife
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game.game_over:
                # Starte das Spiel neu, wenn Space gedrückt wird und Spiel vorbei ist
                game = SnakeGame()

    if not game.game_over:
        # Automatischer Zug, wenn das Spiel läuft
        game.move()  # Nutze move, da es auto_move triggert

    # Zeichne das Spiel, auch wenn game_over, um den Stand zu sehen
    game.draw(screen)  # Übergibt screen korrekt
    pygame.display.flip()
    clock.tick(game.current_speed)