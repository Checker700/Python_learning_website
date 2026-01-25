import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, session, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

DB_Path = 'db/database.db'
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

def init_db():
    os.makedirs('db', exist_ok = True)
    conn = sqlite3.connect(DB_Path)
    # games
    conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            steam_url TEXT,
            description TEXT,
            image_url TEXT
        )
    """)
    # users
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMATY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        )
    """)   
    conn.commit()
    conn.close()

def ensure_admin():
    admin_user = os.environ.get("ADMIN_USERNAME")
    admin_pass = os.environ.get("ADMIN_PASSWORD")
    if not admin_user or not admin_pass:
        return
    
    conn = sqlite3.connect(DB_Path)
    conn.row_factory = sqlite3.Row

    user = conn.execute("SELECT * FROM users WHERE username = ?", (admin_user,)).fetchone()
    if not user:
        conn.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)",
            (admin_user, generate_password_hash(admin_pass))
        )
        conn.commit()
    conn.close()

init_db()
ensure_admin()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        
        conn = sqlite3.connect(DB_Path)
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        conn.close()

        if not user or user["is_admin"] !=1:
            abort(403)

        return fn(*args, **kwargs)
    return wrapper

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = sqlite3.connect(DB_Path)
        conn.row.factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error = "Invalid username or password")
        
        session["user_id"] = user["id"]
        session["usename"] = user["username"]
        return redirect(url_for("admin_home"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

def get_games():
    conn = sqlite3.connect(DB_Path)
    conn.row_factory = sqlite3.Row
    games = conn.execute("""
        SELECT id, title, steam_url, description, image_url
        FROM games
        ORDER BY id DESC
    """).fetchall()
    conn.close()
    return games

@app.route('/')
def index():
    games = get_games()
    return render_template('index.html', games=games)

@app.route("/admin")
@admin_required
def admin_home():
    return render_template("admin.html")

@app.route("/admin/add", methods=["GET", "POST"])
@admin_required
def admin_add_game():
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

        return redirect("admin_delete_page")
    return render_template("add.html")

@app.route("/admin/delete")
@admin_required
def admin_delete_page():
    games = get_games()
    return render_template("delete.html", games=games)

@app.route("/admin/delete/<int:game_id>", methods=["POST"])
def admin_delete_game(game_id):
    conn = sqlite3.connect(DB_Path)
    conn.execute("DELETE FROM games WHERE id = ?", (game_id,))
    conn.commit()
    conn.close()
    return redirect("admin_delete_page")

if __name__ == "__main__": #starting of the app, no code after
    port = port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

