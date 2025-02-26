import pygame
from game import SnakeGame
from constants import *

def run_game():
    print("Log: Initialisiere Spiel")
    game = SnakeGame()
    in_start_screen = True
    while True:
        while in_start_screen:
            game.show_start_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Log: Beende Spiel durch QUIT-Event")
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print(f"Log: Maus-Klick bei Position {event.pos}")
                    if game.manual_button_rect.collidepoint(event.pos):
                        print("Log: Wähle manuellen Modus")
                        game.auto_mode = False
                        in_start_screen = False
                        game.running = True
                    elif game.auto_button_rect.collidepoint(event.pos):
                        print("Log: Wähle Auto-Solve-Modus")
                        game.auto_mode = True
                        in_start_screen = False
                        game.running = True

        while game.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Log: Beende Spiel durch QUIT-Event in Spiel-Schleife")
                    pygame.quit()
                    return
                if not game.auto_mode and event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_w, pygame.K_UP) and game.direction != DOWN:
                        game.direction = UP
                    elif event.key in (pygame.K_s, pygame.K_DOWN) and game.direction != UP:
                        game.direction = DOWN
                    elif event.key in (pygame.K_a, pygame.K_LEFT) and game.direction != RIGHT:
                        game.direction = LEFT
                    elif event.key in (pygame.K_d, pygame.K_RIGHT) and game.direction != LEFT:
                        game.direction = RIGHT
                if game.game_over and event.type == pygame.MOUSEBUTTONDOWN:
                    print(f"Log: Maus-Klick bei game_over bei Position {event.pos}")
                    if game.restart_button_rect.collidepoint(event.pos):
                        print("Log: Neustart ausgelöst")
                        game.reset_game()
                        game.auto_mode = True
                        game.running = True
                        print(f"Log: Nach Reset - running: {game.running}, auto_mode: {game.auto_mode}")
                        break

            if not game.game_over:
                game.move()
            else:
                print(f"Log: Spiel vorbei - game_over: {game.game_over}, running: {game.running}")
            game.render()

        if game.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Log: Beende Spiel durch QUIT-Event nach game_over")
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print(f"Log: Maus-Klick nach game_over bei Position {event.pos}")
                    if game.restart_button_rect.collidepoint(event.pos):
                        print("Log: Neustart nach game_over ausgelöst")
                        game.reset_game()
                        game.auto_mode = True
                        game.running = True
                        print(f"Log: Nach Reset - running: {game.running}, auto_mode: {game.auto_mode}")
                        break

    pygame.quit()

if __name__ == "__main__":
    run_game()