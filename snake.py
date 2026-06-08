import pygame

class Schlange:
    def __init__(self):
        self.x = 10
        self.y = 10
        self.length = 1
        self.direction = "RIGHT"
        self.body = [(self.x, self.y)]
        self.colour = (0, 255, 0)

    def move(self):
        if self.direction == "RIGHT":
            self.x += 1
        elif self.direction == "LEFT":
            self.x -= 1
        elif self.direction == "UP":
            self.y -= 1
        elif self.direction == "DOWN":
            self.y += 1
        self.body.append((self.x, self.y))
        if len(self.body) > self.length:
            self.body.pop(0)

    def change_direction(self, direction):
        if direction == "RIGHT" and self.direction != "LEFT":
            self.direction = "RIGHT"
        elif direction == "LEFT" and self.direction != "RIGHT":
            self.direction = "LEFT"
        elif direction == "UP" and self.direction != "DOWN":
            self.direction = "UP"
        elif direction == "DOWN" and self.direction != "UP":
            self.direction = "DOWN"

    def draw(self, screen, cell_size):
        for part in self.body:
            pygame.draw.rect(screen, self.colour, (part[0] * cell_size, part[1] * cell_size, cell_size, cell_size))