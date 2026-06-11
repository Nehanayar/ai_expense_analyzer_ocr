import sqlite3

DB_PATH = "expense.db"

# ── CONNECTION ────────────────────────────────────────────────────────
def connect_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# ── CREATE TABLES ─────────────────────────────────────────────────────
def create_tables():
    conn = connect_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT    UNIQUE NOT NULL,
        password TEXT    NOT NULL,
        email    TEXT    UNIQUE NOT NULL
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS category (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT    UNIQUE NOT NULL
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id  INTEGER NOT NULL,
        amount   REAL    NOT NULL,
        category TEXT    NOT NULL,
        date     TEXT    NOT NULL
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS budget (
        user_id INTEGER PRIMARY KEY,
        amount  REAL    NOT NULL DEFAULT 0
    )""")

    conn.commit()
    conn.close()


# ── DEFAULT CATEGORIES ────────────────────────────────────────────────
def insert_default_categories():
    defaults = ["Food", "Travel", "Shopping", "Bills", "Health",
                "Fitness", "Insurance", "Entertainment", "Education", "Other"]
    conn = connect_db()
    c = conn.cursor()
    for cat in defaults:
        try:
            c.execute("INSERT INTO category (name) VALUES (?)", (cat,))
        except Exception:
            pass
    conn.commit()
    conn.close()


# ── CATEGORIES ────────────────────────────────────────────────────────
def view_categories():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT name FROM category ORDER BY name")
    data = c.fetchall()
    conn.close()
    return [i[0] for i in data]

def add_category(name):
    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO category (name) VALUES (?)", (name,))
        conn.commit()
        return "Added"
    except Exception:
        return "Exists"
    finally:
        conn.close()


# ── EXPENSES ──────────────────────────────────────────────────────────
def add_expense(user_id, amount, category, date):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
        (user_id, amount, category, date)
    )
    conn.commit()
    conn.close()

def get_expenses(user_id):
    """Returns full rows: id, user_id, amount, category, date"""
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "SELECT id, user_id, amount, category, date FROM expenses WHERE user_id=? ORDER BY date DESC",
        (user_id,)
    )
    data = c.fetchall()
    conn.close()
    return data

def view_expense(user_id):
    """Returns: amount, category, date"""
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "SELECT amount, category, date FROM expenses WHERE user_id=? ORDER BY date DESC",
        (user_id,)
    )
    data = c.fetchall()
    conn.close()
    return data

def delete_expense(expense_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()

def update_expense(expense_id, amount, category, date):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "UPDATE expenses SET amount=?, category=?, date=? WHERE id=?",
        (amount, category, date, expense_id)
    )
    conn.commit()
    conn.close()


# ── BUDGET ────────────────────────────────────────────────────────────
def get_budget(user_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT amount FROM budget WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0.0

def set_budget(user_id, amount):
    conn = connect_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO budget (user_id, amount) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET amount=excluded.amount",
        (user_id, amount)
    )
    conn.commit()
    conn.close()
