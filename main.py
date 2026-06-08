import pygame
from snake import Schlange
from fruit import Fruit
from database import Database

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 600))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.cell_size = 20
        self.db = Database()
        self.player_name = ""
        self.snake = Schlange()
        self.fruit = Fruit()
        self.score = 0
        self.running = True

    def entry_screen(self):
        font = pygame.font.SysFont(None, 42)
        font_small = pygame.font.SysFont(None, 32)
        name = ""

        while True:
            self.screen.fill((0, 0, 0))

            title = font.render("SNAKE", True, (0, 255, 0))
            self.screen.blit(title, (600 // 2 - title.get_width() // 2, 50))

            lb_title = font.render("Leaderboard", True, (255, 255, 255))
            self.screen.blit(lb_title, (600 // 2 - lb_title.get_width() // 2, 120))

            scores = self.db.get_leaderboard()
            if scores:
                for i, (lname, lscore) in enumerate(scores):
                    entry = font_small.render(f"{i+1}. {lname} - {lscore}", True, (255, 255, 255))
                    self.screen.blit(entry, (600 // 2 - entry.get_width() // 2, 170 + i * 35))
            else:
                empty = font_small.render("No scores yet!", True, (150, 150, 150))
                self.screen.blit(empty, (600 // 2 - empty.get_width() // 2, 170))

            prompt = font_small.render(f"Name: {name}", True, (255, 255, 255))
            self.screen.blit(prompt, (600 // 2 - prompt.get_width() // 2, 450))

            hint = font_small.render("Press ENTER to play", True, (150, 150, 150))
            self.screen.blit(hint, (600 // 2 - hint.get_width() // 2, 500))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name.strip():
                        self.player_name = name.strip()
                        return
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        if len(name) < 12:
                            name += event.unicode

    def run(self):
        self.entry_screen()
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
                self.db.add_score(self.player_name, self.score)
                self.losing_screen()
            else:
                self.screen.fill((0, 0, 0))
                self.fruit.draw(self.screen, self.cell_size)
                self.snake.draw(self.screen, self.cell_size)
                pygame.display.flip()

            self.clock.tick(10)

    def losing_screen(self):
        font = pygame.font.SysFont(None, 55)
        font_small = pygame.font.SysFont(None, 36)
        self.screen.fill((0, 0, 0))
        text = font.render(f"Game Over! Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (600 // 2 - text.get_width() // 2, 250))
        hint = font_small.render("ENTER to play again   ESC to quit", True, (150, 150, 150))
        self.screen.blit(hint, (600 // 2 - hint.get_width() // 2, 320))
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
        self.entry_screen()

if __name__ == "__main__":
    game = Game()
    game.run()