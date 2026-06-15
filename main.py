import pygame  # Grafik, Fenster, Events, Audio
import array   # Eingebautes Modul für typisierte Arrays (für Audio-Buffer)
import math    # Eingebautes Modul für sin(), pi() etc.
from snake import Schlange
from fruit import Fruit
from database import Database


def create_eat_sound() -> pygame.mixer.Sound:
    """
    Generiert einen Piep-Soundeffekt ohne externe Datei und ohne numpy.
    Verwendet nur eingebaute Python-Module (math, array).
    """
    # int – Samples pro Sekunde; 44100 = CD-Qualität (Standard)
    sample_rate: int = 44100

    # float – Länge des Tons in Sekunden
    duration: float = 0.12

    # int – Tonhöhe in Hz; 120 Hz = tiefes B ("Bloop"-Klang)
    frequency: int = 120

    # int – Gesamtanzahl der Audio-Samples: 44100 × 0.12 = 5292
    n_samples: int = int(sample_rate * duration)

    # array.array – typisiertes Array mit 16-bit signed integers ("h")
    # *2 weil Stereo: für jeden Sample-Zeitpunkt einen Wert pro Kanal (links + rechts)
    # Startwert: alles 0 (Stille)
    buf: array.array = array.array("h", [0] * (n_samples * 2))

    for i in range(n_samples):
        # Sinuswelle berechnen für Zeitpunkt i:
        # 2π × Frequenz × i/sample_rate = Winkel in Radiant
        # math.sin() → float zwischen -1.0 und +1.0
        # × 32767 → skaliert auf maximalen 16-bit-Wert
        # int() → wandelt float in int (Array akzeptiert nur int)
        val: int = int(math.sin(2 * math.pi * frequency * i / sample_rate) * 32767)

        # Stereo: selben Wert für linken Kanal (gerader Index) und rechten (ungerader Index)
        buf[2 * i]     = val  # linker Kanal
        buf[2 * i + 1] = val  # rechter Kanal

    # pygame.mixer.Sound aus dem Buffer erstellen – kein .wav-File nötig
    return pygame.mixer.Sound(buffer=buf)


class Game:
    """Hauptklasse – koordiniert Game-Loop, alle Screens und alle Spielobjekte."""

    def __init__(self):
        # Mixer VOR pygame.init() konfigurieren, sonst werden Standardwerte verwendet
        # 44100 = Sample-Rate, -16 = 16-bit signed, 2 = Stereo, 512 = Buffer (klein = wenig Verzögerung)
        pygame.mixer.pre_init(44100, -16, 2, 512)

        # Startet alle pygame-Module auf einmal (Display, Events, Mixer, ...)
        pygame.init()

        # pygame.Surface – das Spielfenster; 620 statt 600 Pixel Höhe wegen 20px HUD-Leiste oben
        self.screen: pygame.Surface = pygame.display.set_mode((600, 620))

        # str – Fenstertitel in der Titelleiste
        pygame.display.set_caption("Snake")

        # pygame.time.Clock – begrenzt die Framerate (Spielgeschwindigkeit)
        self.clock: pygame.time.Clock = pygame.time.Clock()

        # int – Größe einer Rasterzelle in Pixeln; 600px / 20px = 30 Felder pro Reihe
        self.cell_size: int = 20

        # Database – Datenbankverbindung (erstellt .db-Datei falls nötig)
        self.db: Database = Database()

        # str – Name des aktuellen Spielers (wird in entry_screen gesetzt)
        self.player_name: str = ""

        # Schlange – neues Schlangen-Objekt mit Startposition
        self.snake: Schlange = Schlange()

        # Fruit – neue Frucht an zufälliger Position
        self.fruit: Fruit = Fruit()

        # int – Punkte der aktuellen Runde
        self.score: int = 0

        # int – bester Score aus der DB; wird live im HUD angezeigt
        self.highscore: int = self._load_highscore()

        # bool – solange True läuft der Game-Loop
        self.running: bool = True

        # pygame.mixer.Sound – Soundeffekt beim Fressen einer Frucht
        self.eat_sound: pygame.mixer.Sound = create_eat_sound()

        # pygame.font.Font – Schriftart für die HUD-Leiste (None = Systemschrift, 28 = Größe)
        self.font_hud: pygame.font.Font = pygame.font.SysFont(None, 28)

    def _load_highscore(self) -> int:
        """Liest den höchsten Score (Platz 1) aus der Datenbank."""
        # list[tuple[str,int]] – Top-5-Liste aus der DB
        scores: list = self.db.get_leaderboard()

        if scores:
            # scores[0] = erster Eintrag (Platz 1) als tuple (name, score)
            # scores[0][1] = zweites Element = der Score-Wert (int)
            return scores[0][1]

        # Noch keine Einträge in der DB → 0 als Startwert
        return 0

    def _draw_hud(self):
        """Zeichnet die Info-Leiste oben: Score (links) und Highscore (rechts)."""

        # Dunklen Hintergrundstreifen für HUD zeichnen
        # (0,0,600,20) = x, y, Breite, Höhe → volle Breite, 20px hoch
        pygame.draw.rect(self.screen, (20, 20, 20), (0, 0, 600, 20))

        # pygame.Surface – gerenderter Text als Bildfläche
        # render(text, antialias, farbe) → antialias=True macht Schrift weicher
        score_text: pygame.Surface = self.font_hud.render(
            f"Score: {self.score}", True, (0, 255, 0)      # grün
        )
        hs_text: pygame.Surface = self.font_hud.render(
            f"Highscore: {self.highscore}", True, (255, 215, 0)  # gold
        )

        # blit() – kopiert eine Surface auf eine andere Surface an Position (x,y)
        self.screen.blit(score_text, (8, 2))  # links, 8px Abstand vom Rand

        # Rechts ausrichten: Fensterbreite - Textbreite - 8px Rand
        # get_width() → int – Breite des gerenderten Textes in Pixeln
        self.screen.blit(hs_text, (600 - hs_text.get_width() - 8, 2))

    def entry_screen(self):
        """Startbildschirm: zeigt Leaderboard und nimmt Spielernamen entgegen."""

        # pygame.font.Font – zwei Schriftgrößen für Titel und normale Texte
        font:       pygame.font.Font = pygame.font.SysFont(None, 42)
        font_small: pygame.font.Font = pygame.font.SysFont(None, 32)

        # str – der gerade eingetippte Name (wächst Buchstabe für Buchstabe)
        name: str = ""

        # Endlosschleife – läuft bis Spieler ENTER drückt
        while True:
            # Bildschirm schwarz füllen (überschreibt vorherigen Frame)
            self.screen.fill((0, 0, 0))

            # Titel "SNAKE" zentrieren:
            # 600//2 = Fenstermitte, - title.get_width()//2 = halbe Textbreite abziehen
            title: pygame.Surface = font.render("SNAKE", True, (0, 255, 0))
            self.screen.blit(title, (600 // 2 - title.get_width() // 2, 50))

            lb_title: pygame.Surface = font.render("Leaderboard", True, (255, 255, 255))
            self.screen.blit(lb_title, (600 // 2 - lb_title.get_width() // 2, 120))

            # list[tuple[str,int]] – Top-5-Scores aus der DB laden
            scores: list = self.db.get_leaderboard()

            if scores:
                # enumerate() gibt Index i und Wert (lname, lscore) gleichzeitig
                # i startet bei 0 → i+1 für Anzeige (Platz 1, 2, 3...)
                for i, (lname, lscore) in enumerate(scores):
                    # f-String kombiniert Index, Name und Score zu einem Text
                    entry: pygame.Surface = font_small.render(
                        f"{i+1}. {lname} - {lscore}", True, (255, 255, 255)
                    )
                    # 170 + i*35 → jeder Eintrag 35px unter dem vorherigen
                    self.screen.blit(entry, (600 // 2 - entry.get_width() // 2, 170 + i * 35))
            else:
                # Noch keine Scores vorhanden
                empty: pygame.Surface = font_small.render("No scores yet!", True, (150, 150, 150))
                self.screen.blit(empty, (600 // 2 - empty.get_width() // 2, 170))

            # Namenseingabe-Zeile anzeigen (aktualisiert sich bei jedem Tastendruck)
            prompt: pygame.Surface = font_small.render(f"Name: {name}", True, (255, 255, 255))
            self.screen.blit(prompt, (600 // 2 - prompt.get_width() // 2, 470))

            hint: pygame.Surface = font_small.render("Press ENTER to play", True, (150, 150, 150))
            self.screen.blit(hint, (600 // 2 - hint.get_width() // 2, 520))

            # flip() – überträgt alles was gezeichnet wurde auf den sichtbaren Bildschirm
            # ohne flip() sieht man nichts!
            pygame.display.flip()

            # Alle Ereignisse (Tastendrücke, Fenster schließen etc.) abarbeiten
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # Fenster-X geklickt
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:  # Taste gedrückt
                    if event.key == pygame.K_RETURN and name.strip():
                        # ENTER + Name nicht leer → Spiel starten
                        # strip() entfernt Leerzeichen am Anfang/Ende des Namens
                        self.player_name = name.strip()  # str
                        return  # Methode verlassen → Spiel beginnt

                    elif event.key == pygame.K_BACKSPACE:
                        # Letztes Zeichen löschen: name[:-1] = alles außer letztem Zeichen
                        name = name[:-1]

                    else:
                        # Buchstabe/Zeichen anhängen, max. 12 Zeichen
                        # event.unicode (str) = der getippte Buchstabe
                        if len(name) < 12:
                            name += event.unicode  # str + str = str

    def run(self):
        """Hauptspielschleife (Game-Loop) – läuft 10× pro Sekunde."""
        self.entry_screen()

        while self.running:  # bool – solange True läuft die Schleife
            # --- 1. EVENTS VERARBEITEN ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False  # Loop beim nächsten Durchlauf beenden

                elif event.type == pygame.KEYDOWN:
                    # Pfeiltasten → Richtung ändern (180°-Kehrtwendung wird in change_direction blockiert)
                    if event.key == pygame.K_RIGHT:
                        self.snake.change_direction("RIGHT")
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction("LEFT")
                    elif event.key == pygame.K_UP:
                        self.snake.change_direction("UP")
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction("DOWN")

            # --- 2. SCHLANGE BEWEGEN ---
            self.snake.move()

            # --- 3. FRUCHT-KOLLISION PRÜFEN ---
            # Tupel-Vergleich: Kopfposition == Fruchtposition?
            if (self.snake.x, self.snake.y) == (self.fruit.x, self.fruit.y):
                self.score += 1         # int – Score erhöhen
                self.snake.length += 1  # int – Schlange wächst beim nächsten move()
                self.fruit.respawn()    # Frucht an neue zufällige Position

                # play() – spielt den Sound ab (non-blocking: Spiel läuft sofort weiter)
                self.eat_sound.play()

                # Highscore live aktualisieren falls aktueller Score besser ist
                if self.score > self.highscore:
                    self.highscore = self.score  # int

            # --- 4. KOLLISION MIT WAND ODER SICH SELBST ---
            # Raster ist 30×30 → gültige Felder: 0–29
            # body[:-1] = ganzer Body OHNE den Kopf (letztes Element)
            # → prüft ob Kopf auf einem anderen Körpersegment liegt
            if (self.snake.x < 0 or self.snake.x >= 30 or
                self.snake.y < 0 or self.snake.y >= 30 or
                (self.snake.x, self.snake.y) in self.snake.body[:-1]):

                # Score in DB speichern und Game-Over-Screen zeigen
                self.db.add_score(self.player_name, self.score)
                self.highscore = self._load_highscore()  # DB neu lesen
                self.losing_screen()

            else:
                # --- 5. SPIELFELD ZEICHNEN ---
                self.screen.fill((0, 0, 0))  # Schwarzer Hintergrund
                self._draw_hud()             # HUD-Leiste oben zeichnen

                # Schlange zeichnen mit +20px Y-Offset wegen HUD-Leiste
                for part in self.snake.body:  # part: tuple[int,int]
                    pygame.draw.rect(
                        self.screen,
                        self.snake.colour,
                        (
                            part[0] * self.cell_size,
                            part[1] * self.cell_size + 20,  # +20 = HUD-Offset
                            self.cell_size,
                            self.cell_size
                        )
                    )

                # Frucht zeichnen ebenfalls mit +20px Y-Offset
                pygame.draw.rect(
                    self.screen,
                    self.fruit.colour,
                    (
                        self.fruit.x * self.cell_size,
                        self.fruit.y * self.cell_size + 20,  # +20 = HUD-Offset
                        self.cell_size,
                        self.cell_size
                    )
                )

                # flip() – fertigen Frame auf den Bildschirm übertragen
                pygame.display.flip()

            # tick(10) – begrenzt Loop auf 10 Durchläufe/Sekunde = Spielgeschwindigkeit
            # ohne tick() würde das Spiel mit hunderten FPS unkontrollierbar schnell laufen
            self.clock.tick(10)

    def losing_screen(self):
        """Game-Over-Bildschirm – ENTER = neues Spiel, ESC = beenden."""

        font:       pygame.font.Font = pygame.font.SysFont(None, 55)
        font_small: pygame.font.Font = pygame.font.SysFont(None, 36)

        self.screen.fill((0, 0, 0))

        # f-String zeigt den erreichten Score im Text
        text: pygame.Surface = font.render(
            f"Game Over! Score: {self.score}", True, (255, 255, 255)
        )
        # Zentriert bei Y=250
        self.screen.blit(text, (600 // 2 - text.get_width() // 2, 250))

        hint: pygame.Surface = font_small.render(
            "ENTER to play again   ESC to quit", True, (150, 150, 150)
        )
        self.screen.blit(hint, (600 // 2 - hint.get_width() // 2, 320))
        pygame.display.flip()

        # Warten bis Spieler eine Taste drückt
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
                        self.reset()  # Spiel zurücksetzen
                        return        # losing_screen verlassen → zurück zu run()

    def reset(self):
        """Setzt alle Spielobjekte zurück und zeigt den Startbildschirm."""
        self.snake = Schlange()  # Neue Schlange-Instanz
        self.fruit = Fruit()     # Neue Frucht-Instanz
        self.score = 0           # int – Score auf 0
        self.running = True      # bool – Game-Loop wieder aktivieren
        self.entry_screen()      # Namenseingabe erneut anzeigen


# Wird nur ausgeführt wenn diese Datei direkt gestartet wird (python main.py)
# Beim Import als Modul ist __name__ nicht "__main__" → Game() startet nicht automatisch
if __name__ == "__main__":
    game: Game = Game()
    game.run()
