import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_FILE = os.path.join(BASE_DIR, "traffic.db")


def init_db():
    connection = sqlite3.connect(DB_FILE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicles INTEGER,
            hour INTEGER,
            day INTEGER,
            weather INTEGER,
            traffic REAL,
            congestion TEXT,
            signal_time INTEGER,
            created_at TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_prediction(
    vehicles,
    hour,
    day,
    weather,
    traffic,
    congestion,
    signal_time
):
    connection = sqlite3.connect(DB_FILE)

    connection.execute("""
        INSERT INTO predictions
        (
            vehicles,
            hour,
            day,
            weather,
            traffic,
            congestion,
            signal_time,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        vehicles,
        hour,
        day,
        weather,
        traffic,
        congestion,
        signal_time,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()
    connection.close()


def get_predictions():
    connection = sqlite3.connect(DB_FILE)

    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT *
        FROM predictions
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return [dict(row) for row in rows]