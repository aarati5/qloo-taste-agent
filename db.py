import sqlite3

DB_PATH = "passport.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS favourites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            qloo_id TEXT
        )""")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS consent (
            user_id TEXT NOT NULL,
            category TEXT NOT NULL,
            allowed INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (user_id, category)
        )""")
    conn.commit()
    conn.close()


def add_favourite(user_id, category, name, qloo_id=None):
    conn = get_conn()
    conn.execute(
        "INSERT INTO favourites (user_id, category, name, qloo_id) VALUES (?, ?, ?, ?)",
        (user_id, category, name, qloo_id),
    )
    conn.commit()
    conn.close()


def get_favourites(user_id, only_allowed=False):
    conn = get_conn()
    if only_allowed:
        rows = conn.execute(
            """SELECT f.* FROM favourites f
               LEFT JOIN consent c
                 ON c.user_id = f.user_id AND c.category = f.category
               WHERE f.user_id = ? AND COALESCE(c.allowed, 1) = 1""",
            (user_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM favourites WHERE user_id = ?", (user_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_consent(user_id, category, allowed):
    conn = get_conn()
    conn.execute(
        """INSERT INTO consent (user_id, category, allowed) VALUES (?, ?, ?)
           ON CONFLICT(user_id, category) DO UPDATE SET allowed = excluded.allowed""",
        (user_id, category, int(allowed)),
    )
    conn.commit()
    conn.close()


def get_consent(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT category, allowed FROM consent WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return {r["category"]: bool(r["allowed"]) for r in rows}

def seed_demo():
    """Fill the demo profile if empty (free hosting resets the database)."""
    conn = get_conn()
    n = conn.execute(
        "SELECT COUNT(*) FROM favourites WHERE user_id = 'demo'"
    ).fetchone()[0]
    conn.close()
    if n == 0:
        for cat, name in [("music", "Radiohead"), ("movies", "Her"),
                          ("food", "Biryani"), ("travel", "Hampi")]:
            add_favourite("demo", cat, name)
        set_consent("demo", "food", False)

def seed_user(user_id: str):
    """Give a new visitor their own copy of the demo profile."""
    conn = get_conn()
    n = conn.execute(
        "SELECT COUNT(*) FROM favourites WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    conn.close()
    if n == 0:
        for cat, name in [("music", "Radiohead"), ("movies", "Her"),
                          ("food", "Biryani"), ("travel", "Hampi")]:
            add_favourite(user_id, cat, name)
        set_consent(user_id, "food", False)