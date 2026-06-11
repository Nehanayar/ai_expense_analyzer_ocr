import sqlite3
import bcrypt
from database import connect_db


# ── REGISTER ─────────────────────────────────────────────────────────
def register(username, password, email):
    conn = connect_db()
    c = conn.cursor()

    username = username.strip()
    email    = email.strip().lower()
    password = password.strip()

    if not username or not password or not email:
        conn.close()
        return "Empty"

    try:
        c.execute("SELECT id FROM users WHERE username=?", (username,))
        if c.fetchone():
            return "Username Exists"

        c.execute("SELECT id FROM users WHERE email=?", (email,))
        if c.fetchone():
            return "Email Exists"

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        c.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, hashed, email)
        )
        conn.commit()
        return "Success"

    except sqlite3.Error as e:
        return f"Error: {e}"

    finally:
        conn.close()


# ── LOGIN ─────────────────────────────────────────────────────────────
def login(email, password):
    conn = connect_db()
    c = conn.cursor()

    email    = email.strip().lower()
    password = password.strip()

    if not email or not password:
        conn.close()
        return None

    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()

    if user:
        stored_pwd = user[2]
        if isinstance(stored_pwd, str):
            stored_pwd = stored_pwd.encode()
        if bcrypt.checkpw(password.encode(), stored_pwd):
            return user

    return None
