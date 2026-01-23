import os
import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

DB_Path = 'db/database.db'

def init_db():
    os.makedirs('db', exist_ok = True)
    conn = sqlite3.connect(DB_Path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            steam_url TEXT,
            description TEXT,
            image_url TEXT
        )
    """)   
    conn.commit()
    conn.close()

init_db()

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
    return render_template('index.html', games=games)

@app.route("/add", methods=["GET", "POST"])

def add_game():
    if request.method == 'POST':
        #print("FORM DATA:", request.form) #simple request check

        title = request.form.get('title')
        steam_url = request.form.get("steam_url")
        description = request.form.get('description')
        image_url = request.form.get('image_url')

        if not title or not steam_url: #simple check
            return "Title and Steam URL are required", 400

        conn = sqlite3.connect(DB_Path)
        conn.execute("""
            INSERT INTO games (title, steam_url, description, image_url)
            VALUES (?, ?, ?, ?)
        """, (title, steam_url, description, image_url))
        conn.commit()
        conn.close()

        return redirect("/")
    return render_template("add.html")

@app.route("/delete")
def delete_page():
    game = get_games()
    return render_template("delete.html", games=game)

@app.route("/delete/<int:game_id>", methods=["POST"])
def delete_game(game_id):
    conn = sqlite3.connect(DB_Path)
    conn.execute("DELETE FROM games WHERE id = ?", (game_id))
    conn.commit()
    conn.close()
    return redirect("/delete")

if __name__ == "__main__": #starting of the app, no code after
    port = port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

