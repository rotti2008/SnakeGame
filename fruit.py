import random as r
import pygame

class Fruit:
    def __init__(self):
        self.x = r.randint(0, 29)
        self.y = r.randint(0, 29)
        self.colour = (255, 0, 0)
    def respawn(self):
        self.x = r.randint(0, 29)
        self.y = r.randint(0, 29)
    def draw(self, screen, cell_size):
        pygame.draw.rect(screen, self.colour, (self.x * cell_size, self.y * cell_size, cell_size, cell_size))