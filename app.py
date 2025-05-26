import os
import sqlite3
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from functools import wraps
from werkzeug.security import generate_password_hash

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = os.urandom(24)

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
	return render_template("index.html")

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

if __name__ == "__main__":
    app.run(debug=True)
