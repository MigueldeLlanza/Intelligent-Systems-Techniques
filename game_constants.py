import pygame

"""
.py file where all the game constants are stored
"""

# Board and square sizes
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Board color
WHITISH = (230, 230, 230)
BROWN = (138, 120, 93)

# Selected piece
RED = (255, 100, 0, 130)

# Valid moves
BLUE = (0, 100, 255, 130)

# Pieces color
BLACK = (0, 0, 0)
WHITE = (250, 250, 250)

# Piece edge color
GREY = (128, 128, 128)

# King's crown image
CROWN = pygame.transform.scale(pygame.image.load('crown.png'), (30, 30))