import pygame
import sys

# --- Initialisierung ---
pygame.init()

BREITE, HOEHE = 600, 400
HINTERGRUND = (30, 30, 30)      # Dunkelgrau
SPIELER_FARBE = (0, 200, 255)   # Cyan
FPS = 60
GESCHWINDIGKEIT = 5

# Fenster erstellen
fenster = pygame.display.set_mode((BREITE, HOEHE))
pygame.display.set_caption("Pygame Minimal – Pfeiltasten zum Bewegen")
uhr = pygame.time.Clock()

# --- Spieler-Rechteck (x, y, breite, hoehe) ---
spieler = pygame.Rect(BREITE // 2 - 25, HOEHE // 2 - 25, 50, 50)

# --- Hauptschleife ---
while True:
    # 1) Events abfragen (z. B. Fenster schließen)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    # 2) Gedrückte Tasten kontinuierlich abfragen
    tasten = pygame.key.get_pressed()
    if tasten[pygame.K_LEFT]:
        spieler.x -= GESCHWINDIGKEIT
    if tasten[pygame.K_RIGHT]:
        spieler.x += GESCHWINDIGKEIT
    if tasten[pygame.K_UP]:
        spieler.y -= GESCHWINDIGKEIT
    if tasten[pygame.K_DOWN]:
        spieler.y += GESCHWINDIGKEIT

    # 3) Spieler innerhalb des Fensters halten (Clamp)
    spieler.clamp_ip(pygame.Rect(0, 0, BREITE, HOEHE))

    # 4) Zeichnen
    fenster.fill(HINTERGRUND)                          # Hintergrund löschen
    pygame.draw.rect(fenster, SPIELER_FARBE, spieler)  # Spieler zeichnen

    # Kleine Hilfstext-Anzeige
    font = pygame.font.SysFont("monospace", 16)
    text = font.render("Pfeiltasten zum Bewegen  |  ESC = Beenden", True, (180, 180, 180))
    fenster.blit(text, (10, 10))

    # 5) Bild anzeigen & FPS begrenzen
    pygame.display.flip()
    uhr.tick(FPS)
