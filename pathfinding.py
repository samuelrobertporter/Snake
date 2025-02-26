# pathfinding.py
from heapq import heappush, heappop
from utils import heuristic, get_neighbors

def a_star(start, goal, width, height, snake):
    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = heappop(open_set)[1]
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        for neighbor in get_neighbors(current, width, height, snake):
            tentative_g_score = g_score[current] + 20  # GRID_SIZE
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heappush(open_set, (f_score[neighbor], neighbor))
    print("A* Pfad nicht gefunden")
    return None

def follow_tail(head, snake, width, height):
    tail = snake[-1]
    best_neighbor = None
    min_dist = float('inf')
    neighbors = get_neighbors(head, width, height, snake)
    for neighbor in neighbors:
        if neighbor not in snake[1:-1]:
            dist = heuristic(neighbor, tail)
            if dist < min_dist:
                min_dist = dist
                best_neighbor = neighbor
    print(f"Follow_tail: head={head}, tail={tail}, best_neighbor={best_neighbor}, neighbors={neighbors}")
    return best_neighbor

def generate_snake_path(width, height, rows, cols):
    path = []
    for row in range(rows):
        if row % 2 == 0:
            for col in range(cols):
                path.append((col * 20, row * 20))  # GRID_SIZE
        else:
            for col in reversed(range(cols)):
                path.append((col * 20, row * 20))
    return path

def find_closest_path_index(head, path):
    min_dist = float('inf')
    closest_index = 0
    for i, pos in enumerate(path):
        dist = heuristic(head, pos)
        if dist < min_dist:
            min_dist = dist
            closest_index = i
    return closest_index