import random as r  # Modul für Zufallszahlen; Kurzname "r" für weniger Tipparbeit
import pygame        # Bibliothek für Grafik


class Fruit:
    """Repräsentiert die Frucht (Ziel) im Snake-Spiel."""

    def __init__(self):
        # int – zufällige Startposition auf dem 30×30-Raster (0 bis 29)
        # r.randint(a,b) → gibt zufälligen int zwischen a und b zurück (beide inkl.)
        self.x: int = r.randint(0, 29)
        self.y: int = r.randint(0, 29)

        # tuple[int,int,int] – RGB-Farbe: (255,0,0) = reines Rot
        self.colour: tuple = (255, 0, 0)

    def respawn(self):
        """Setzt die Frucht an eine neue zufällige Position (nach dem Fressen)."""

        # Neue Zufallsposition auf dem Raster
        # Hinweis: Es wird nicht geprüft ob die Position frei ist
        # → Frucht könnte theoretisch im Schlangenkörper spawnen
        self.x: int = r.randint(0, 29)
        self.y: int = r.randint(0, 29)

    def draw(self, screen: pygame.Surface, cell_size: int):
        """
        Zeichnet die Frucht als rotes Rechteck auf den Bildschirm.

        Args:
            screen (pygame.Surface): Das Spielfenster
            cell_size (int): Größe einer Rasterzelle in Pixeln
        """
        # Rasterkoordinate × cell_size = Pixelposition
        # z.B. Feld (5,3) bei cell_size=20 → Pixel (100, 60)
        pygame.draw.rect(
            screen,
            self.colour,
            (
                self.x * cell_size,   # int – X-Pixelposition
                self.y * cell_size,   # int – Y-Pixelposition
                cell_size,            # int – Breite
                cell_size             # int – Höhe
            )
        )
