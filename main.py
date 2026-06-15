import pygame
import array
import math
from snake import Schlange
from fruit import Fruit
from database import Database


def create_eat_sound():
    """
    Generiert einen kurzen Soundeffekt (Piep) ohne numpy und ohne externe Datei.

    Funktionsweise:
    - Berechnet eine Sinuswelle mit dem eingebauten 'math'-Modul (kein numpy!).
    - Speichert die Samples im eingebauten 'array'-Modul als 16-bit signed int.
    - Stereo: jeder Sample wird zweimal gespeichert (links + rechts).
    - pygame.mixer.Sound() akzeptiert direkt ein bytes-Objekt.

    Returns:
        pygame.mixer.Sound: Abspielbarer Soundeffekt.
    """
    sample_rate = 44100
    duration = 0.12      # Sekunden
    frequency = 120      # Hz (hohes A – klingt nach "Pling")

    n_samples = int(sample_rate * duration)
    buf = array.array("h", [0] * (n_samples * 2))  # *2 für Stereo

    for i in range(n_samples):
        val = int(math.sin(2 * math.pi * frequency * i / sample_rate) * 32767)
        buf[2 * i] = val      # linker Kanal
        buf[2 * i + 1] = val  # rechter Kanal
    print(type(pygame.mixer.Sound(buffer=buf)))  # Debug: Überprüfen des Sound-Objekttyps
    return pygame.mixer.Sound(buffer=buf)


class Game:
    """
    Hauptklasse des Snake-Spiels. Koordiniert alle anderen Module
    und enthält den Game-Loop sowie alle Screens.

    Attributes:
        screen (pygame.Surface): Das Spielfenster (600×620 Pixel).
        clock (pygame.time.Clock): Steuert die Framerate (Spielgeschwindigkeit).
        cell_size (int): Größe einer Rasterzelle in Pixeln (20 → 30×30-Raster).
        db (Database): Datenbankzugriff für Scores.
        player_name (str): Name des aktuellen Spielers.
        snake (Schlange): Die Schlange des Spielers.
        fruit (Fruit): Die aktuelle Frucht auf dem Spielfeld.
        score (int): Aktueller Punktestand dieser Runde.
        highscore (int): Bester Score aus der Datenbank (wird live angezeigt).
        running (bool): Steuert den Game-Loop (False = Spiel endet).
        eat_sound (pygame.mixer.Sound): Soundeffekt beim Fressen einer Frucht.
    """

    def __init__(self):
        """
        Initialisiert pygame (inkl. Audio-Mixer), erstellt das Fenster
        und alle Spielobjekte. Lädt den Highscore aus der Datenbank.
        """
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()

        # 620 statt 600 Pixel Höhe: 20px extra oben für die Score-Leiste
        self.screen = pygame.display.set_mode((600, 620))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.cell_size = 20

        self.db = Database()
        self.player_name = ""
        self.snake = Schlange()
        self.fruit = Fruit()
        self.score = 0
        self.highscore = self._load_highscore()
        self.running = True

        self.eat_sound = create_eat_sound()
        self.font_hud = pygame.font.SysFont(None, 28)

    def _load_highscore(self):
        """
        Liest den aktuellen Highscore (Platz 1) aus der Datenbank.

        Returns:
            int: Höchster bisher gespeicherter Score, oder 0 falls keine Einträge.
        """
        scores = self.db.get_leaderboard()
        if scores:
            return scores[0][1]  # (name, score) → nur score
        return 0

    def _draw_hud(self):
        """
        Zeichnet die HUD-Leiste (Heads-Up-Display) am oberen Rand des Fensters.

        Zeigt links den aktuellen Score und rechts den Highscore an.
        Das Spielfeld ist um 20px nach unten verschoben (offset), damit
        die HUD-Leiste nicht vom Spielfeld überlappt wird.
        """
        # Dunkler Hintergrundstreifen für die HUD
        pygame.draw.rect(self.screen, (20, 20, 20), (0, 0, 600, 20))

        score_text = self.font_hud.render(f"Score: {self.score}", True, (0, 255, 0))
        hs_text = self.font_hud.render(f"Highscore: {self.highscore}", True, (255, 215, 0))

        self.screen.blit(score_text, (8, 2))
        self.screen.blit(hs_text, (600 - hs_text.get_width() - 8, 2))

    def entry_screen(self):
        """
        Zeigt den Startbildschirm mit Leaderboard und Namenseingabe.

        Ablauf:
        - Zeichnet Titel, Top-5-Leaderboard und ein Texteingabefeld.
        - Der Spieler tippt seinen Namen (max. 12 Zeichen).
        - BACKSPACE löscht das letzte Zeichen.
        - ENTER bestätigt den Namen und startet das Spiel (nur wenn Name nicht leer).

        Setzt self.player_name auf den eingegebenen Namen.
        """
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
            self.screen.blit(prompt, (600 // 2 - prompt.get_width() // 2, 470))

            hint = font_small.render("Press ENTER to play", True, (150, 150, 150))
            self.screen.blit(hint, (600 // 2 - hint.get_width() // 2, 520))

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
        """
        Hauptspielschleife (Game-Loop).

        Ablauf pro Frame (10× pro Sekunde via clock.tick(10)):
        1. Events verarbeiten (Tastatureingaben für Richtungsänderung).
        2. Schlange bewegen.
        3. Kollision mit Frucht prüfen:
           → Score erhöhen, Sound abspielen, Schlange wächst, Frucht neu spawnen.
           → Highscore live aktualisieren falls übertroffen.
        4. Kollision mit Wand oder sich selbst prüfen → Game Over.
        5. Spielfeld neu zeichnen: Hintergrund, HUD, Frucht, Schlange.
        """
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

            # Frucht gefressen?
            if (self.snake.x, self.snake.y) == (self.fruit.x, self.fruit.y):
                self.score += 1
                self.snake.length += 1
                self.fruit.respawn()
                self.eat_sound.play()  # 🔊 Soundeffekt abspielen

                # Highscore live aktualisieren
                if self.score > self.highscore:
                    self.highscore = self.score

            # Wand- oder Selbstkollision?
            if (self.snake.x < 0 or self.snake.x >= 30 or
                self.snake.y < 0 or self.snake.y >= 30 or
                (self.snake.x, self.snake.y) in self.snake.body[:-1]):
                self.db.add_score(self.player_name, self.score)
                self.highscore = self._load_highscore()  # DB-Highscore neu laden
                self.losing_screen()
            else:
                # Spielfeld zeichnen (20px Offset wegen HUD)
                self.screen.fill((0, 0, 0))
                self._draw_hud()

                # Spielfeld ist 20px nach unten verschoben
                # → fruit und snake müssen mit offset gezeichnet werden
                for part in self.snake.body:
                    pygame.draw.rect(
                        self.screen,
                        self.snake.colour,
                        (part[0] * self.cell_size,
                         part[1] * self.cell_size + 20,  # +20 wegen HUD
                         self.cell_size, self.cell_size)
                    )
                pygame.draw.rect(
                    self.screen,
                    self.fruit.colour,
                    (self.fruit.x * self.cell_size,
                     self.fruit.y * self.cell_size + 20,  # +20 wegen HUD
                     self.cell_size, self.cell_size)
                )
                pygame.display.flip()

            self.clock.tick(10)

    def losing_screen(self):
        """
        Zeigt den Game-Over-Bildschirm mit dem erreichten Score.

        Optionen:
        - ENTER: Neues Spiel starten (ruft reset() auf).
        - ESC oder Fenster schließen: Spiel beenden.
        """
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
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
                    elif event.key == pygame.K_RETURN:
                        self.reset()
                        return

    def reset(self):
        """
        Setzt das Spiel auf den Ausgangszustand zurück für eine neue Runde.

        Erstellt neue Schlange und Frucht, setzt Score auf 0,
        und zeigt erneut den entry_screen().
        """
        self.snake = Schlange()
        self.fruit = Fruit()
        self.score = 0
        self.running = True
        self.entry_screen()


if __name__ == "__main__":
    game = Game()
    game.run()
