import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("snake_scores.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                score INTEGER NOT NULL,
                FOREIGN KEY(player_id) REFERENCES players(id)
            )
        """)
        self.conn.commit()

    def add_score(self, name, score):
        self.cursor.execute("SELECT id FROM players WHERE name = ?", (name,))
        player = self.cursor.fetchone()
        if player:
            player_id = player[0]
        else:
            self.cursor.execute("INSERT INTO players (name) VALUES (?)", (name,))
            player_id = self.cursor.lastrowid
        self.cursor.execute("INSERT INTO scores (player_id, score) VALUES (?, ?)", (player_id, score))
        self.conn.commit()

    def get_leaderboard(self):
        self.cursor.execute("""
            SELECT players.name, MAX(scores.score) as best_score
            FROM scores
            JOIN players ON scores.player_id = players.id
            GROUP BY players.id
            ORDER BY best_score DESC
            LIMIT 5
        """)
        return self.cursor.fetchall()