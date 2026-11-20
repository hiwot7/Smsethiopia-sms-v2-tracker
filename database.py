import sqlite3
from datetime import datetime

DB_NAME = "reminders.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            msisdn TEXT NOT NULL,
            message_text TEXT NOT NULL,
            sms_ulid TEXT UNIQUE,
            segments INTEGER DEFAULT 0,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()