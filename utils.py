# utils.py
def heuristic(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def get_neighbors(pos, width, height, snake):
    x, y = pos
    possible = [
        (x + 20, y),  # GRID_SIZE ist 20
        (x - 20, y),
        (x, y + 20),
        (x, y - 20)
    ]
    return [p for p in possible if 0 <= p[0] < width and 0 <= p[1] < height and p not in snake[1:]]

def get_safe_next_step(head, target, width, height, snake):
    x, y = head
    tx, ty = target
    possible_steps = [
        ((x + 20, y), (1, 0)),  # RIGHT
        ((x - 20, y), (-1, 0)),  # LEFT
        ((x, y + 20), (0, 1)),  # DOWN
        ((x, y - 20), (0, -1))  # UP
    ]
    
    valid_steps = []
    for next_pos, direction in possible_steps:
        if (0 <= next_pos[0] < width and 
            0 <= next_pos[1] < height and 
            next_pos not in snake):
            dist = heuristic(next_pos, target)
            valid_steps.append((dist, next_pos, direction))
    
    if valid_steps:
        valid_steps.sort()
        return valid_steps[0][1]  # next_pos
    return None