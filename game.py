import pygame
import random
import os
from constants import *
from utils import get_safe_next_step, get_neighbors
from pathfinding import a_star, follow_tail, generate_snake_path, find_closest_path_index

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake 🐍")
        self.clock = pygame.time.Clock()

        self.visited = set()
        self.base_speed = 20  # Für 240 cm/min bei GRID_SIZE = 20
        self.current_speed = self.base_speed
        self.path_fail_count = 0  # Zähler für nicht gefundene Pfade
        self.reset_game()
        self.highscores = self.load_highscores()
        self.coverage_history = self.load_coverage_history()
        self.last_scores = self.load_last_scores()

        self.manual_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 40, 200, 40)
        self.auto_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 40)
        self.restart_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 40)

    def reset_game(self):
        self.running = True
        self.score = 0
        self.path = generate_snake_path(WIDTH, HEIGHT, ROWS, COLS)
        self.snake = [self.path[0]]
        self.food = self.spawn_food()
        self.direction = RIGHT
        self.game_over = False
        self.path_index = 0
        self.max_length = 1
        self.auto_mode = False
        self.current_speed = self.base_speed
        self.path_fail_count = 0
        self.visited = set([self.path[0]])
        print("Spiel zurückgesetzt")
        print(f"Startposition: {self.snake[0]}, Futter: {self.food}")

    def spawn_food(self):
        attempts = 0
        while attempts < 20:
            food_pos = (random.randint(0, COLS-1) * GRID_SIZE, 
                        random.randint(0, ROWS-1) * GRID_SIZE)
            if food_pos not in self.snake and a_star(self.snake[0], food_pos, WIDTH, HEIGHT, self.snake):
                return food_pos
            attempts += 1
        # Fallback: Nächstes freies Feld nahe am Kopf
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
        # Änderung: Deckung basiert jetzt auf der maximalen Länge der Schlange
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
            self.auto_move()
        else:
            self.manual_move()

    def is_safe_move(self, new_head, snake, width, height, log=True):
        """Sicherheitsprüfung nur auf Kollision."""
        if (new_head[0] < 0 or new_head[0] >= WIDTH or 
            new_head[1] < 0 or new_head[1] >= HEIGHT or 
            new_head in snake):
            if log:
                print(f"Log: Kollision oder außerhalb bei {new_head}")
            return False
        return True

    def is_adjacent(self, pos1, pos2):
        """Prüft, ob zwei Positionen benachbart sind."""
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2) == GRID_SIZE

    def auto_move(self):
        if self.game_over or len(self.snake) >= TOTAL_CELLS:
            if not self.game_over:
                self.game_over = True
                self.running = False
                self.save_highscores()
                self.save_last_scores()
                self.save_coverage_history()
                # Log-Anpassung: Zeigt die Deckung basierend auf max_length
                print(f"Log: Spielende erreicht, Score: {self.score}, Coverage: {(self.max_length / TOTAL_CELLS) * 100:.1f}%")
            return

        head = self.snake[0]
        new_head = None

        # Debug: Aktueller Zustand
        print(f"Debug: Head bei {head}, Länge: {len(self.snake)}, Futter: {self.food}, Score: {self.score}")

        # Schritt 1: Direkt zum Futter
        path_to_food = a_star(head, self.food, WIDTH, HEIGHT, self.snake)
        print(f"Debug: Path to food: {path_to_food[:2] if path_to_food else None}")
        if path_to_food and len(path_to_food) > 1:
            potential_new_head = path_to_food[1]
            if (self.is_adjacent(head, potential_new_head) and 
                self.is_safe_move(potential_new_head, self.snake, WIDTH, HEIGHT)):
                new_head = potential_new_head
                self.current_speed = self.base_speed
                self.path_fail_count = 0  # Reset bei Erfolg
                print(f"Log: Futter erreicht bei {new_head}, Score: {self.score + 1}")
            else:
                print(f"Log: Unsicherer oder nicht benachbarter Zug zum Futter bei {potential_new_head}")
        else:
            self.path_fail_count += 1
            self.current_speed = max(self.base_speed / (1 + self.path_fail_count * 0.5), 1)
            print("A* Pfad nicht gefunden")
            if self.path_fail_count > 5:
                self.food = self.spawn_food()
                self.path_fail_count = 0

        # Schritt 2: Raum maximieren mit Randstrafe
        if not new_head:
            neighbors = get_neighbors(head, WIDTH, HEIGHT, self.snake)
            print(f"Debug: Neighbors: {neighbors}")
            max_score = -float('inf')
            best_neighbor = None
            for neighbor in neighbors:
                if neighbor not in self.snake:
                    reachable = self.count_reachable(neighbor, self.snake)
                    food_dist = abs(neighbor[0] - self.food[0]) + abs(neighbor[1] - self.food[1])
                    edge_penalty = (min(neighbor[0], WIDTH - neighbor[0]) + min(neighbor[1], HEIGHT - neighbor[1])) / GRID_SIZE
                    score = reachable * 2 - food_dist / GRID_SIZE + edge_penalty  # Randstrafe hinzufügen
                    if score > max_score and self.is_safe_move(neighbor, self.snake, WIDTH, HEIGHT):
                        max_score = score
                        best_neighbor = neighbor
            if best_neighbor:
                new_head = best_neighbor
                self.current_speed = self.base_speed
                self.path_fail_count = max(0, self.path_fail_count - 1)
                print(f"Log: Raum maximiert bei {new_head}, Erreichbare Felder: {self.count_reachable(new_head, self.snake)}")
            else:
                self.path_fail_count += 1
                self.current_speed = max(self.base_speed / (1 + self.path_fail_count * 0.5), 1)
                print(f"Log: Kein optimaler Nachbar bei {head}, Nachbarn: {neighbors}")

        # Schritt 3: Nächster Hamilton-Zyklus-Punkt
        if not new_head and self.path_index + 1 < len(self.path):
            next_step = self.find_next_path_point(head)
            print(f"Debug: Next Hamilton point: {next_step}")
            if (next_step and 
                self.is_adjacent(head, next_step) and 
                self.is_safe_move(next_step, self.snake, WIDTH, HEIGHT)):
                new_head = next_step
                self.path_index = self.path.index(next_step)
                self.current_speed = self.base_speed
                self.path_fail_count = max(0, self.path_fail_count - 1)
                print(f"Log: Hamilton-Zyklus bei {new_head}")
            else:
                print(f"Log: Unsicherer oder nicht benachbarter Zug im Hamilton-Zyklus bei {next_step}")

        # Schritt 4: Fallback auf Schwanz
        if not new_head:
            path_to_tail = a_star(head, self.snake[-1], WIDTH, HEIGHT, self.snake)
            print(f"Debug: Path to tail: {path_to_tail[:2] if path_to_tail else None}")
            if path_to_tail and len(path_to_tail) > 1:
                potential_new_head = path_to_tail[1]
                if (self.is_adjacent(head, potential_new_head) and 
                    self.is_safe_move(potential_new_head, self.snake, WIDTH, HEIGHT)):
                    new_head = potential_new_head
                    self.current_speed = self.base_speed
                    self.path_fail_count = max(0, self.path_fail_count - 1)
                    print(f"Log: Sicherer Zug zum Schwanz bei {new_head}")
                else:
                    self.path_fail_count += 1
            else:
                self.path_fail_count += 1
                self.current_speed = max(self.base_speed / (1 + self.path_fail_count * 0.5), 1)
                print("A* Pfad nicht gefunden")

        # Schritt 5: Letzter Ausweg
        if not new_head:
            neighbors = get_neighbors(head, WIDTH, HEIGHT, self.snake)
            print(f"Debug: Notfall-Neighbors: {neighbors}")
            max_reachable = -1
            best_neighbor = None
            for neighbor in neighbors:
                if neighbor not in self.snake and self.is_adjacent(head, neighbor):
                    reachable = self.count_reachable(neighbor, self.snake)
                    food_dist = abs(neighbor[0] - self.food[0]) + abs(neighbor[1] - self.food[1])
                    score = reachable - food_dist / GRID_SIZE
                    if reachable > max_reachable or (reachable == max_reachable and score > max_reachable):
                        max_reachable = reachable
                        best_neighbor = neighbor
            if best_neighbor:
                new_head = best_neighbor
                self.current_speed = self.base_speed
                self.path_fail_count = max(0, self.path_fail_count - 1)
                print(f"Log: Notfall-Zug bei {new_head}, Erreichbare Felder: {max_reachable}")
            else:
                self.path_fail_count += 1
                self.current_speed = max(self.base_speed / (1 + self.path_fail_count * 0.5), 1)

        # Schritt 6: Spielende
        if not new_head or new_head == head or new_head in self.snake:
            if not self.game_over:
                self.game_over = True
                self.running = False
                self.save_highscores()
                self.save_last_scores()
                self.save_coverage_history()
                # Log-Anpassung: Zeigt die Deckung basierend auf max_length
                print(f"Log: Sackgasse oder Kollision bei {head}, new_head={new_head}, Coverage: {(self.max_length / TOTAL_CELLS) * 100:.1f}%")
            return

        # Schritt 7: Bewege Schlange
        self.snake.insert(0, new_head)
        self.visited.add(new_head)
        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
            self.max_length = max(self.max_length, len(self.snake))
        else:
            self.snake.pop()

    def find_next_path_point(self, current_pos):
        """Finde den nächstgelegenen Punkt im Hamilton-Zyklus."""
        closest_dist = float('inf')
        closest_point = None
        for i, point in enumerate(self.path[self.path_index + 1:], start=self.path_index + 1):
            dist = abs(point[0] - current_pos[0]) + abs(point[1] - current_pos[1])  # Manhattan-Distanz
            if dist < closest_dist and point not in self.snake:
                closest_dist = dist
                closest_point = point
                self.path_index = i
        return closest_point

    def count_reachable(self, start, snake, max_depth=20):
        """Zählt erreichbare Felder mit begrenzter Tiefe."""
        visited = set(snake)
        queue = [(start, 0)]  # (Position, Tiefe)
        count = 0
        while queue:
            pos, depth = queue.pop(0)
            if pos not in visited and depth <= max_depth:
                visited.add(pos)
                count += 1
                for neighbor in get_neighbors(pos, WIDTH, HEIGHT, snake):
                    if neighbor not in visited and neighbor not in self.snake:
                        queue.append((neighbor, depth + 1))
        return count

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
            self.running = False
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

    def draw_text(self, text, x, y, size=24, color=WHITE):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def render(self):
        self.screen.fill(BLACK)
        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN, (*segment, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(self.screen, RED, (*self.food, GRID_SIZE, GRID_SIZE))

        self.draw_text(f"Punkte: {self.score}", 10, 10, 24, WHITE)
        self.draw_text(f"Durchschn. Deckung (letzte 10): {self.get_average_coverage():.1f}%", 10, 40, 20, GREEN)
        self.draw_text(f"Tempo: {self.get_speed_cm_per_min():.1f} cm/min", 10, 60, 20, YELLOW)
        
        self.draw_text("Top 5 High-Scores:", WIDTH - 200, 10, 24, YELLOW)
        for i, score in enumerate(self.highscores):
            self.draw_text(f"{i+1}. {score}", WIDTH - 200, 40 + i * 20, 20, YELLOW)

        self.draw_text("Letzte 5 Scores:", 10, HEIGHT - 120, 24, YELLOW)
        for i, score in enumerate(self.last_scores):
            self.draw_text(f"{i+1}. {score}", 10, HEIGHT - 90 + i * 20, 20, YELLOW)

        if self.game_over:
            self.draw_text("Game Over!", WIDTH // 2 - 60, HEIGHT // 3, 32, WHITE)
            pygame.draw.rect(self.screen, YELLOW, self.restart_button_rect)
            self.draw_text("Neustart", WIDTH // 2 - 40, HEIGHT // 2 + 70, 22, BLACK)

        pygame.display.flip()
        self.clock.tick(self.current_speed)

    def show_start_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("Snake Game", WIDTH // 2 - 50, HEIGHT // 3, 32, WHITE)
        self.draw_text("Wähle einen Modus:", WIDTH // 2 - 80, HEIGHT // 2 - 70, 24, WHITE)

        pygame.draw.rect(self.screen, BLUE, self.manual_button_rect)
        self.draw_text("Manueller Modus", WIDTH // 2 - 80, HEIGHT // 2 - 30, 22, WHITE)

        pygame.draw.rect(self.screen, GREEN, self.auto_button_rect)
        self.draw_text("Auto-Solve Modus", WIDTH // 2 - 80, HEIGHT // 2 + 20, 22, WHITE)

        pygame.display.flip()