import pygame  # Bibliothek für Grafik, Fenster, Tastatureingaben


class Schlange:
    """Repräsentiert die steuerbare Schlange im Snake-Spiel."""

    def __init__(self):
        # int – Startposition des Kopfes auf dem Raster (Feld 10 von 30)
        self.x: int = 10
        self.y: int = 10

        # int – Länge der Schlange in Segmenten; startet mit 1
        self.length: int = 1

        # str – aktuelle Bewegungsrichtung; mögliche Werte: "RIGHT","LEFT","UP","DOWN"
        self.direction: str = "RIGHT"

        # list[tuple[int,int]] – Liste aller Körpersegmente als (x,y)-Koordinaten
        # Index 0 = Schwanz, letzter Index = Kopf
        self.body: list = [(self.x, self.y)]

        # tuple[int,int,int] – RGB-Farbe der Schlange: (Rot, Grün, Blau)
        # (0,255,0) = reines Grün
        self.colour: tuple = (0, 255, 0)

    def move(self):
        """Bewegt die Schlange einen Schritt in die aktuelle Richtung."""

        # Kopfposition je nach Richtung um 1 Rasterfeld verschieben
        # ACHTUNG: In pygame ist Y=0 oben → UP bedeutet y-1, DOWN bedeutet y+1
        if self.direction == "RIGHT":
            self.x += 1   # int + int → int
        elif self.direction == "LEFT":
            self.x -= 1
        elif self.direction == "UP":
            self.y -= 1   # Y-Achse invertiert! Oben = kleinerer Wert
        elif self.direction == "DOWN":
            self.y += 1

        # Neue Kopfposition ans Ende der Body-Liste anhängen
        # tuple(int,int) wird in list eingefügt
        self.body.append((self.x, self.y))

        # Schwanz entfernen wenn Body länger als erlaubte Länge
        # → Schlange "wandert": neues Segment vorne, altes hinten weg
        # len() → int; pop(0) entfernt Index 0 (ältestes = Schwanz)
        if len(self.body) > self.length:
            self.body.pop(0)

    def change_direction(self, direction: str):
        """
        Ändert die Richtung – verhindert 180°-Kehrtwendung.

        Args:
            direction (str): Gewünschte neue Richtung
        """
        # Gegenrichtungen werden blockiert (z.B. RIGHT ↔ LEFT)
        # → verhindert dass Schlange sofort in sich selbst fährt
        if direction == "RIGHT" and self.direction != "LEFT":
            self.direction = "RIGHT"
        elif direction == "LEFT" and self.direction != "RIGHT":
            self.direction = "LEFT"
        elif direction == "UP" and self.direction != "DOWN":
            self.direction = "UP"
        elif direction == "DOWN" and self.direction != "UP":
            self.direction = "DOWN"

    def draw(self, screen: pygame.Surface, cell_size: int):
        """
        Zeichnet alle Segmente der Schlange als Rechtecke.

        Args:
            screen (pygame.Surface): Das Spielfenster
            cell_size (int): Größe einer Rasterzelle in Pixeln
        """
        # Jedes Segment in der Body-Liste einzeln zeichnen
        for part in self.body:  # part: tuple[int, int]
            # Rasterkoordinate → Pixelkoordinate: Raster * cell_size
            # z.B. Feld (10,5) bei cell_size=20 → Pixel (200, 100)
            pygame.draw.rect(
                screen,
                self.colour,
                (
                    part[0] * cell_size,   # int – X-Pixelposition
                    part[1] * cell_size,   # int – Y-Pixelposition
                    cell_size,             # int – Breite des Rechtecks
                    cell_size              # int – Höhe des Rechtecks
                )
            )
