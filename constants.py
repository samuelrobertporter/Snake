# constants.py
# Fenstergröße
WIDTH = 600
HEIGHT = 400
GRID_SIZE = 20
ROWS = HEIGHT // GRID_SIZE
COLS = WIDTH // GRID_SIZE
TOTAL_CELLS = ROWS * COLS

# Farben (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Richtungsvorgaben
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)