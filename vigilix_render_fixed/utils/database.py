import os
import sqlite3

# On Render the working directory may be read-only; /tmp is always writable.
# Set DB_PATH env var to override (e.g. for a mounted disk).
DB_PATH = os.environ.get("DB_PATH", "/tmp/vigilix.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            gmail TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS cameras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            camera_name TEXT NOT NULL,
            location TEXT NOT NULL,
            location_type TEXT NOT NULL,
            source TEXT NOT NULL,
            alert_email TEXT,
            status TEXT DEFAULT 'Active',
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            camera_id INTEGER,
            threat_type TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            confidence TEXT,
            evidence_path TEXT,
            alert_date TEXT,
            alert_day TEXT,
            alert_time TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
