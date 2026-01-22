import os
import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

DB_Path = 'db/database.db'

def init_db():
    os.makedirs('db', exist_ok = True)
    conn = sqlite3.connect(DB_Path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            steam_url TEXT NOT NULL
        )
    """)   
    conn.commit()
    conn.close()

def get_games():
    conn = sqlite3.connect(DB_Path)
    conn.row_factory = sqlite3.Row
    games = conn.execute("""
        SELECT title, steam_url, description, image_url
        FROM games
    """).fetchall()
    conn.close()
    return games

@app.route('/')
def index():
    games = get_games()
    return render_template('index.html', games = games)

if __name__ == "__main__":
    init_db()
    port = port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

