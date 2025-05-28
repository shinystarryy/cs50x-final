import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = "dev-secret-key"

def apology(message, code=400):
    return render_template("apology.html", top=code, bottom=message), code

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    conn = sqlite3.connect("todo.db")
    db = conn.cursor()

    db.execute("SELECT id, content, timestamp, description, priority, due_date FROM todos WHERE user_id = ? AND completed = 0 ORDER BY timestamp DESC", (user_id,))
    incomplete_tasks = db.fetchall()

    db.execute("SELECT id, content, timestamp, description, priority, due_date FROM todos WHERE user_id = ? AND completed = 1 ORDER BY timestamp DESC", (user_id,))
    completed_tasks = db.fetchall()

    db.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    username = db.fetchone()[0]

    conn.close()

    incomplete_tasks = [{"id": t[0], "content": t[1], "timestamp": t[2], "description": t[3], "priority": t[4], "due_date": t[5]} for t in incomplete_tasks]
    completed_tasks = [{"id": t[0], "content": t[1], "timestamp": t[2], "description": t[3], "priority": t[4], "due_date": t[5]} for t in completed_tasks]

    return render_template("index.html", username=username, incomplete_tasks=incomplete_tasks, completed_tasks=completed_tasks)

@app.route("/add_task", methods=["POST"])
@login_required
def add_task():
    content = request.form.get("content")
    description = request.form.get("description")
    priority = request.form.get("priority")
    due_date = request.form.get("due_date")
    
    if not content:
        return apology("must provide task content", 400)
    if not priority:
        return apology("must select task priority", 400)
    
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            return apology("invalid date format", 400)
    
    user_id = session["user_id"]
    conn = sqlite3.connect("todo.db")
    db = conn.cursor()

    db.execute("INSERT INTO todos (user_id, content, description, priority, due_date) VALUES (?, ?, ?, ?, ?)", (user_id, content, description, priority, due_date))

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/delete_task/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    user_id = session["user_id"]
    conn = sqlite3.connect("todo.db")
    db = conn.cursor()

    db.execute("DELETE FROM todos WHERE id = ? AND user_id = ?", (task_id, user_id))

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
    
        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confirmation:
            return apology("must confirm password", 400)
        elif password != confirmation:
            return apology("passwords do not match", 400)
        
        hash_pw = generate_password_hash(password)

        conn = sqlite3.connect("todo.db")
        db = conn.cursor()

        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash_pw))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return apology("username already exists", 400)

        db.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = db.fetchone()
        conn.close()

        session["user_id"] = user[0]
        return redirect("/")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)

        conn = sqlite3.connect("todo.db")
        db = conn.cursor()

        db.execute("SELECT id, hash FROM users WHERE username = ?", (username,))
        user = db.fetchone()
        conn.close()

        if user is None or not check_password_hash(user[1], password):
            return apology("invalid username and/or password", 400)

        session["user_id"] = user[0]
        return redirect("/")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
