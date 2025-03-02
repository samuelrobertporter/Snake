import pygame
import os
import random
from constants import *
from auto_move import auto_move, simulate_snake_after_move, find_next_path_point, count_reachable

class SnakeGame:
    def __init__(self):
        # Keine Parameterübergabe nötig, da Konstanten aus constants.py genutzt werden
        pygame.display.set_caption("Snake 🐍")
        self.clock = pygame.time.Clock()

        self.visited = set()
        self.base_speed = 20  # Für 240 cm/min bei GRID_SIZE = 20
        self.current_speed = self.base_speed
        self.path_fail_count = 0
        self.reset_game()
        self.highscores = self.load_highscores()
        self.coverage_history = self.load_coverage_history()
        self.last_scores = self.load_last_scores()

        self.manual_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 40, 200, 40)
        self.auto_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 40)
        self.restart_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 40)

    def reset_game(self):
        self.running = True  # Bleibt True, Fenster wird in main.py gesteuert
        self.score = 0
        from pathfinding import generate_snake_path
        self.path = generate_snake_path(WIDTH, HEIGHT, ROWS, COLS)
        self.snake = [self.path[0]]
        self.food = self.spawn_food()
        self.direction = RIGHT
        self.game_over = False
        self.path_index = 0
        self.max_length = 1
        self.auto_mode = True  # Geändert auf True für Auto-Modus als Standard
        self.current_speed = self.base_speed
        self.path_fail_count = 0
        self.visited = set([self.path[0]])
        print("Spiel zurückgesetzt")
        print(f"Startposition: {self.snake[0]}, Futter: {self.food}")

    def spawn_food(self):
        from pathfinding import a_star
        attempts = 0
        while attempts < 20:
            food_pos = (random.randint(0, COLS-1) * GRID_SIZE, 
                        random.randint(0, ROWS-1) * GRID_SIZE)
            if food_pos not in self.snake and a_star(self.snake[0], food_pos, WIDTH, HEIGHT, self.snake):
                return food_pos
            attempts += 1
        head_x, head_y = self.snake[0]
        for dx in range(-10, 11):
            for dy in range(-10, 11):
                food_pos = (head_x + dx * GRID_SIZE, head_y + dy * GRID_SIZE)
                if (0 <= food_pos[0] < WIDTH and 0 <= food_pos[1] < HEIGHT and 
                    food_pos not in self.snake):
                    return food_pos
        for x in range(COLS):
            for y in range(ROWS):
                food_pos = (x * GRID_SIZE, y * GRID_SIZE)
                if food_pos not in self.snake:
                    return food_pos
        return None

    def load_highscores(self):
        if os.path.exists("highscores.txt"):
            with open("highscores.txt", "r") as file:
                scores = [int(line.strip()) for line in file.readlines() if line.strip()]
                return sorted(scores, reverse=True)[:5]
        return [0] * 5

    def save_highscores(self):
        self.highscores.append(self.score)
        self.highscores = sorted(self.highscores, reverse=True)[:5]
        with open("highscores.txt", "w") as file:
            for score in self.highscores:
                file.write(f"{score}\n")

    def load_coverage_history(self):
        if os.path.exists("coverage_history.txt"):
            with open("coverage_history.txt", "r") as file:
                history = [float(line.strip()) for line in file.readlines() if line.strip()]
                return history[-10:]
        return []

    def save_coverage_history(self):
        coverage = (self.max_length / TOTAL_CELLS) * 100
        self.coverage_history.append(coverage)
        if len(self.coverage_history) > 10:
            self.coverage_history.pop(0)
        with open("coverage_history.txt", "w") as file:
            for cov in self.coverage_history:
                file.write(f"{cov}\n")

    def load_last_scores(self):
        if os.path.exists("last_scores.txt"):
            with open("last_scores.txt", "r") as file:
                scores = [int(line.strip()) for line in file.readlines() if line.strip()]
                return scores[-5:]
        return [0] * 5

    def save_last_scores(self):
        self.last_scores.append(self.score)
        if len(self.last_scores) > 5:
            self.last_scores.pop(0)
        with open("last_scores.txt", "w") as file:
            for score in self.last_scores:
                file.write(f"{score}\n")

    def get_average_coverage(self):
        if not self.coverage_history:
            return 0.0
        return sum(self.coverage_history) / len(self.coverage_history)

    def move(self):
        if self.game_over:
            return
        if self.auto_mode:
            auto_move(self)
        else:
            self.manual_move()

    def manual_move(self):
        if self.game_over:
            return

        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx * GRID_SIZE, head_y + dy * GRID_SIZE)

        if (new_head[0] < 0 or new_head[0] >= WIDTH or
            new_head[1] < 0 or new_head[1] >= HEIGHT or
            new_head in self.snake):
            self.game_over = True
            # self.running bleibt True, damit das Fenster offen bleibt
            self.save_highscores()
            self.save_last_scores()
            self.save_coverage_history()
            print(f"Log: Manuelle Kollision bei {new_head}, Schlange={self.snake[:5]}...")
            return

        self.snake.insert(0, new_head)
        self.visited.add(new_head)

        if new_head == self.food:
            self.food = self.spawn_food()
            self.score += 1
            self.max_length = max(self.max_length, len(self.snake))
        else:
            self.snake.pop()

    def get_speed_cm_per_min(self):
        speed_cm_per_sec = self.current_speed * GRID_SIZE / 100
        return speed_cm_per_sec * 60

    def draw_text(self, screen, text, x, y, size=24, color=WHITE):  # screen als Parameter
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))  # Nutze screen statt self.screen

    def draw(self, screen):  # screen als Parameter
        screen.fill(BLACK)
        for segment in self.snake:
            pygame.draw.rect(screen, GREEN, (*segment, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, RED, (*self.food, GRID_SIZE, GRID_SIZE))

        self.draw_text(screen, f"Punkte: {self.score}", 10, 10, 24, WHITE)
        self.draw_text(screen, f"Durchschn. Deckung (letzte 10): {self.get_average_coverage():.1f}%", 10, 40, 20, GREEN)
        self.draw_text(screen, f"Tempo: {self.get_speed_cm_per_min():.1f} cm/min", 10, 60, 20, YELLOW)
        
        self.draw_text(screen, "Top 5 High-Scores:", WIDTH - 200, 10, 24, YELLOW)
        for i, score in enumerate(self.highscores):
            self.draw_text(screen, f"{i+1}. {score}", WIDTH - 200, 40 + i * 20, 20, YELLOW)

        self.draw_text(screen, "Letzte 5 Scores:", 10, HEIGHT - 120, 24, YELLOW)
        for i, score in enumerate(self.last_scores):
            self.draw_text(screen, f"{i+1}. {score}", 10, HEIGHT - 90 + i * 20, 20, YELLOW)

        if self.game_over:
            self.draw_text(screen, "Game Over!", WIDTH // 2 - 60, HEIGHT // 3, 32, WHITE)
            pygame.draw.rect(screen, YELLOW, self.restart_button_rect)
            self.draw_text(screen, "Neustart", WIDTH // 2 - 40, HEIGHT // 2 + 70, 22, BLACK)

    def show_start_screen(self, screen):  # screen als Parameter
        screen.fill(BLACK)
        self.draw_text(screen, "Snake Game", WIDTH // 2 - 50, HEIGHT // 3, 32, WHITE)
        self.draw_text(screen, "Wähle einen Modus:", WIDTH // 2 - 80, HEIGHT // 2 - 70, 24, WHITE)

        pygame.draw.rect(screen, BLUE, self.manual_button_rect)
        self.draw_text(screen, "Manueller Modus", WIDTH // 2 - 80, HEIGHT // 2 - 30, 22, WHITE)

        pygame.draw.rect(screen, GREEN, self.auto_button_rect)
        self.draw_text(screen, "Auto-Solve Modus", WIDTH // 2 - 80, HEIGHT // 2 + 20, 22, WHITE)