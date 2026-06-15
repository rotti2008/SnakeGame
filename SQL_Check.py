import sqlite3
conn = sqlite3.connect('snake_scores.db')
c = conn.cursor()

c.execute("SELECT * from scores")
print(c.fetchall())