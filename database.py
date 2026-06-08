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