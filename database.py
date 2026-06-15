import sqlite3  # Eingebautes Modul für SQLite-Datenbanken (kein extra Install nötig)


class Database:
    """
    Verwaltet die SQLite-Datenbank für Spielernamen und Highscores.

    Tabellenstruktur:
        players: id (int, auto), name (text)
        scores:  id (int, auto), player_id (int, FK), timestamp (datetime), score (int)
    """

    def __init__(self):
        # sqlite3.Connection – öffnet/erstellt die Datei "snake_scores.db" im Projektordner
        # Datei wird automatisch angelegt falls sie noch nicht existiert
        self.conn: sqlite3.Connection = sqlite3.connect("snake_scores.db")

        # sqlite3.Cursor – Werkzeug zum Ausführen von SQL-Befehlen
        # conn = Datenbankverbindung, cursor = "Stift" zum Schreiben/Lesen
        self.cursor: sqlite3.Cursor = self.conn.cursor()

        # Tabelle "players" erstellen – nur wenn sie noch nicht existiert
        # IF NOT EXISTS → kein Fehler beim zweiten Programmstart
        # AUTOINCREMENT → id wird automatisch hochgezählt (1, 2, 3, ...)
        # NOT NULL → Feld darf nicht leer sein
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players(
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT    NOT NULL
            )
        """)

        # Tabelle "scores" erstellen
        # FOREIGN KEY → player_id muss auf eine echte id in "players" zeigen
        # DEFAULT CURRENT_TIMESTAMP → Datum/Uhrzeit wird automatisch gesetzt
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores(
                id        INTEGER  PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER  NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                score     INTEGER  NOT NULL,
                FOREIGN KEY(player_id) REFERENCES players(id)
            )
        """)

        # commit() – speichert alle Änderungen dauerhaft in die Datei
        # ohne commit() gehen Änderungen verloren!
        self.conn.commit()

    def add_score(self, name: str, score: int):
        """
        Speichert einen neuen Score für einen Spieler.

        Ablauf:
        1. Prüfen ob Spielername schon in players existiert
        2a. Ja → vorhandene id verwenden
        2b. Nein → neuen Spieler anlegen, neue id holen
        3. Score-Eintrag in scores einfügen

        Args:
            name  (str): Spielername
            score (int): Erreichte Punktzahl
        """
        # SELECT – sucht den Spieler in der Tabelle
        # ? = Platzhalter (Prepared Statement) → verhindert SQL-Injection
        # (name,) = Tupel mit einem Element; das Komma macht es zum Tupel!
        self.cursor.execute("SELECT id FROM players WHERE name = ?", (name,))

        # fetchone() → gibt eine Zeile als tuple zurück, oder None wenn nichts gefunden
        player: tuple | None = self.cursor.fetchone()

        if player:
            # Spieler existiert bereits → seine id aus dem Ergebnis-Tupel holen
            # player[0] = erster Wert der Zeile = die id (int)
            player_id: int = player[0]
        else:
            # Neuer Spieler → in players einfügen
            self.cursor.execute("INSERT INTO players (name) VALUES (?)", (name,))
            # lastrowid (int) → die automatisch vergebene id des gerade eingefügten Eintrags
            player_id: int = self.cursor.lastrowid

        # Score-Eintrag speichern; zwei Platzhalter ? für player_id und score
        self.cursor.execute(
            "INSERT INTO scores (player_id, score) VALUES (?, ?)",
            (player_id, score)
        )

        # Änderungen dauerhaft speichern
        self.conn.commit()

    def get_leaderboard(self) -> list:
        """
        Gibt die Top-5 Spieler nach bestem Score zurück.

        SQL-Erklärung:
            MAX(scores.score)   → höchster Score pro Spieler
            JOIN                → verknüpft players und scores über player_id
            GROUP BY players.id → fasst alle Scores eines Spielers zusammen
            ORDER BY DESC       → absteigend sortieren (höchster Score zuerst)
            LIMIT 5             → nur die Top 5

        Returns:
            list[tuple[str, int]]: z.B. [("Rotti", 42), ("Max", 17), ...]
        """
        self.cursor.execute("""
            SELECT players.name, MAX(scores.score) AS best_score
            FROM scores
            JOIN players ON scores.player_id = players.id
            GROUP BY players.id
            ORDER BY best_score DESC
            LIMIT 5
        """)

        # fetchall() → gibt ALLE Ergebniszeilen als list[tuple] zurück
        # im Gegensatz zu fetchone() das nur eine Zeile holt
        return self.cursor.fetchall()
