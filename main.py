import pygame
from snake import Schlange
from fruit import Fruit

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 600))
        self.clock = pygame.time.Clock()
        self.cell_size = 20
        self.snake = Schlange()
        self.fruit = Fruit()
        self.score = 0
        self.running = True

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.snake.change_direction("RIGHT")
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction("LEFT")
                    elif event.key == pygame.K_UP:
                        self.snake.change_direction("UP")
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction("DOWN")

            self.snake.move()

            if (self.snake.x, self.snake.y) == (self.fruit.x, self.fruit.y):
                self.score += 1
                self.snake.length += 1
                self.fruit.respawn()

            if (self.snake.x < 0 or self.snake.x >= 30 or
                self.snake.y < 0 or self.snake.y >= 30 or
                (self.snake.x, self.snake.y) in self.snake.body[:-1]):
                self.losing_screen()
            else:
                self.screen.fill((0, 0, 0))
                self.fruit.draw(self.screen, self.cell_size)
                self.snake.draw(self.screen, self.cell_size)
                pygame.display.flip()

            self.clock.tick(10)

        print(f"Game Over! Your score: {self.score}")

    def losing_screen(self):
        font = pygame.font.SysFont(None, 55)
        text = font.render(f"Game Over! Your score: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (50, 250))
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    elif event.key == pygame.K_RETURN:
                        self.reset()
                        return

    def reset(self):
        self.snake = Schlange()
        self.fruit = Fruit()
        self.score = 0
        self.running = True

if __name__ == "__main__":
    game = Game()
    game.run()