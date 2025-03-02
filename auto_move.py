from constants import *
from utils import get_neighbors
from pathfinding import a_star, generate_snake_path

def is_safe_move(new_head, snake, width, height, log=True):
    if (new_head[0] < 0 or new_head[0] >= width or 
        new_head[1] < 0 or new_head[1] >= height or 
        new_head in snake):
        if log:
            print(f"Log: Kollision oder außerhalb bei {new_head}")
        return False
    return True

def is_adjacent(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x1 - x2) + abs(y1 - y2) == GRID_SIZE

def simulate_snake_after_move(self, new_head, eat_food=False):
    new_snake = self.snake.copy()
    new_snake.insert(0, new_head)
    if not eat_food:
        new_snake.pop()
    print(f"Debug: Simulated snake: {new_snake[:5]}...")
    return new_snake

def generate_strategic_route():
    route = []
    for y in range(0, HEIGHT, GRID_SIZE):
        if y % (2 * GRID_SIZE) == 0:  # Gerade Zeilen: links nach rechts
            for x in range(0, WIDTH - GRID_SIZE, GRID_SIZE):  # Bis x=560, x=580 frei
                route.append((x, y))
        else:  # Ungerade Zeilen: rechts nach links
            for x in range(WIDTH - 2 * GRID_SIZE, -GRID_SIZE, -GRID_SIZE):  # Von 560 nach 0
                route.append((x, y))
    return route

def find_next_strategic_point(self, current_pos, route):
    for i, point in enumerate(route):
        if is_adjacent(current_pos, point) and point not in self.snake:
            print(f"Debug: Strategische Route - Aktuell: {current_pos}, Nächster Punkt: {point}, Index: {i}")
            return point, i
    print(f"Debug: Kein benachbarter strategischer Punkt für {current_pos}")
    return None, None

def count_reachable(self, start, snake, max_depth=50):
    visited = set(snake)
    queue = [(start, 0)]
    count = 0
    while queue and count < TOTAL_CELLS:
        pos, depth = queue.pop(0)
        if pos not in visited and depth <= max_depth:
            visited.add(pos)
            count += 1
            for neighbor in get_neighbors(pos, WIDTH, HEIGHT, snake):
                if neighbor not in visited and neighbor not in snake:
                    queue.append((neighbor, depth + 1))
    print(f"Debug: Erreichbare Felder von {start} mit Schlange {snake[:5]}...: {count}")
    return count

def auto_move(self):
    if self.game_over or len(self.snake) >= TOTAL_CELLS:
        if not self.game_over:
            self.game_over = True
            print(f"Log: Spielende erreicht, Score: {self.score}, Coverage: {(self.max_length / TOTAL_CELLS) * 100:.1f}%")
        return

    head = self.snake[0]
    new_head = None
    recent_moves = self.snake[:10]

    print(f"Debug: Head bei {head}, Länge: {len(self.snake)}, Futter: {self.food}, Score: {self.score}")

    # Strategische Route ab Länge 81 (80 Punkte)
    if len(self.snake) >= 81:
        if not hasattr(self, 'strategic_route'):
            self.strategic_route = generate_strategic_route()
            self.route_index = 0
        # Zum Startpunkt (0, 0) navigieren, falls nicht dort
        if head != (0, 0):
            path_to_start = a_star(head, (0, 0), WIDTH, HEIGHT, self.snake)
            if path_to_start and len(path_to_start) > 1:
                new_head = path_to_start[1]
                if is_adjacent(head, new_head) and is_safe_move(new_head, self.snake, WIDTH, HEIGHT):
                    print(f"Log: Navigiere zu Startpunkt bei {new_head}")
                else:
                    new_head = None
        else:
            # Folge der strategischen Route
            next_point, index = find_next_strategic_point(self, head, self.strategic_route)
            if next_point and is_safe_move(next_point, self.snake, WIDTH, HEIGHT):
                new_head = next_point
                self.route_index = index + 1
                print(f"Log: Strategische Route bei {new_head}")

    # Schritt 1: Futterjagd (bis Länge 80)
    if not new_head and len(self.snake) < 81:
        path_to_food = a_star(head, self.food, WIDTH, HEIGHT, self.snake)
        print(f"Debug: Path to food: {path_to_food[:2] if path_to_food else 'None'}")
        if path_to_food and len(path_to_food) > 1:
            potential_new_head = path_to_food[1]
            if is_adjacent(head, potential_new_head) and is_safe_move(potential_new_head, self.snake, WIDTH, HEIGHT):
                simulated_snake = simulate_snake_after_move(self, potential_new_head, eat_food=True)
                food_dist = abs(head[0] - self.food[0]) + abs(head[1] - self.food[1])
                max_food_dist = TOTAL_CELLS - len(self.snake)
                if food_dist < max_food_dist:
                    new_head = potential_new_head
                    self.current_speed = self.base_speed
                    self.path_fail_count = 0
                    print(f"Log: Sicherer Zug zum Futter bei {new_head}, Score: {self.score + 1}")
                else:
                    print(f"Log: Futter bei {self.food} zu weit (Distanz: {food_dist}, Max: {max_food_dist})")
            else:
                print(f"Log: Unsicherer oder nicht benachbarter Zug zum Futter bei {potential_new_head}")
        else:
            print("A* Pfad zum Futter nicht gefunden")
            self.path_fail_count += 1
            if self.path_fail_count > 5:
                self.food = self.spawn_food()
                self.path_fail_count = 0

    # Schritt 2: Raum maximieren (Fallback bis 80)
    if not new_head and len(self.snake) < 81:
        neighbors = get_neighbors(head, WIDTH, HEIGHT, self.snake)
        print(f"Debug: Neighbors: {neighbors}")
        max_score = -float('inf')
        best_neighbor = None
        tail = self.snake[-1]
        for neighbor in neighbors:
            if neighbor not in self.snake and is_adjacent(head, neighbor):
                if neighbor in recent_moves and len(neighbors) > 1:
                    print(f"Debug: Skipping {neighbor} - recently visited")
                    continue
                simulated_snake = simulate_snake_after_move(self, neighbor)
                reachable = count_reachable(self, neighbor, simulated_snake)
                food_dist = abs(neighbor[0] - self.food[0]) + abs(neighbor[1] - self.food[1])
                tail_dist = abs(neighbor[0] - tail[0]) + abs(neighbor[1] - tail[1])
                is_at_wall = head[0] == 0 or head[0] == WIDTH - GRID_SIZE or head[1] == 0 or head[1] == HEIGHT - GRID_SIZE
                center_bonus = 50 * (abs(neighbor[0] - WIDTH // 2) + abs(neighbor[1] - HEIGHT // 2)) / (WIDTH + HEIGHT)
                wall_penalty = -200 if is_at_wall and head[1] == neighbor[1] else 0
                vertical_bonus = 100 if head[1] != neighbor[1] else 0
                tail_weight = 5 if is_at_wall and head[0] != neighbor[0] else (20 if is_at_wall else 2)
                score = reachable + vertical_bonus - food_dist / GRID_SIZE + tail_dist / tail_weight + wall_penalty - center_bonus
                print(f"Debug: Nachbar {neighbor} - Score: {score}, Erreichbare Felder: {reachable}, Tail-Dist: {tail_dist}")
                if score > max_score and is_safe_move(neighbor, self.snake, WIDTH, HEIGHT):
                    max_score = score
                    best_neighbor = neighbor
        if best_neighbor:
            new_head = best_neighbor
            self.current_speed = self.base_speed
            self.path_fail_count = max(0, self.path_fail_count - 1)
            print(f"Log: Raum maximiert bei {new_head}")
        else:
            self.path_fail_count += 1
            self.current_speed = max(self.base_speed / (1 + self.path_fail_count * 0.5), 1)
            print(f"Log: Kein optimaler Nachbar bei {head}, Nachbarn: {neighbors}")

    # Schritt 3: Hamilton-Zyklus (Fallback bis 80)
    if not new_head and len(self.snake) < 81:
        if not hasattr(self, 'path'):
            self.path = generate_snake_path(WIDTH, HEIGHT, ROWS, COLS)
            self.path_index = 0
        next_step = find_next_path_point(self, head)
        if next_step and is_safe_move(next_step, self.snake, WIDTH, HEIGHT):
            new_head = next_step
            self.path_index += 1
            self.current_speed = self.base_speed
            self.path_fail_count = max(0, self.path_fail_count - 1)
            print(f"Log: Hamilton-Zyklus bei {new_head}")
        else:
            if self.path_fail_count > 5:
                self.path = generate_snake_path(WIDTH, HEIGHT, ROWS, COLS)
                self.path_index = 0
                self.path_fail_count = 0
                print("Debug: Hamilton-Pfad zurückgesetzt wegen zu vieler Fehlschläge")

    # Schritt 4: Notfall-Zug
    if not new_head:
        neighbors = get_neighbors(head, WIDTH, HEIGHT, self.snake)
        print(f"Debug: Notfall-Neighbors: {neighbors}")
        for neighbor in neighbors:
            if neighbor not in self.snake and is_adjacent(head, neighbor):
                if neighbor not in recent_moves and is_safe_move(neighbor, self.snake, WIDTH, HEIGHT):
                    new_head = neighbor
                    self.current_speed = self.base_speed
                    self.path_fail_count = max(0, self.path_fail_count - 1)
                    print(f"Log: Notfall-Zug bei {new_head}")
                    break
        else:
            self.path_fail_count += 1
            self.current_speed = max(self.base_speed / (1 + self.path_fail_count * 0.5), 1)
            print("Log: Kein Notfall-Zug möglich")

    # Schritt 5: Spielende
    if not new_head or new_head == head or new_head in self.snake:
        if not self.game_over:
            self.game_over = True
            print(f"Log: Sackgasse oder Kollision bei {head}, new_head={new_head}, Coverage: {(self.max_length / TOTAL_CELLS) * 100:.1f}%")
        return

    # Schritt 6: Bewege Schlange
    self.snake.insert(0, new_head)
    self.visited.add(new_head)
    if new_head == self.food:
        self.score += 1
        self.food = self.spawn_food()
        self.max_length = max(self.max_length, len(self.snake))
        if len(self.snake) >= 81:
            next_hamilton = find_next_strategic_point(self, new_head, self.strategic_route)[0]
            if next_hamilton:
                self.route_index -= 1
        print(f"Log: Futter gegessen, neue Position: {new_head}")
    else:
        self.snake.pop()
        print(f"Log: Schritt gemacht zu {new_head}")