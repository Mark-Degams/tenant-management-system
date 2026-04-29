import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            room_num     TEXT NOT NULL UNIQUE,
            room_type    TEXT NOT NULL CHECK(room_type IN ('Solo','Bedspacer')),
            capacity     INTEGER NOT NULL,
            deposit      REAL NOT NULL,
            rent_summer  REAL NOT NULL,
            rent_regular REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tenants (
            tenant_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name  TEXT NOT NULL,
            last_name   TEXT NOT NULL,
            contact_num TEXT NOT NULL,
            birthdate   TEXT NOT NULL,
            sex         TEXT NOT NULL CHECK(sex IN ('Male','Female','Other'))
        );
                         
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id  INTEGER NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
            amount     REAL NOT NULL,
            due_date   TEXT NOT NULL,
            pay_date   TEXT,
            status     TEXT NOT NULL DEFAULT 'Pending'
                           CHECK(status IN ('Pending','Paid','Overdue'))
        );

        CREATE TABLE IF NOT EXISTS rental_agreements (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id    INTEGER NOT NULL REFERENCES rooms(room_id) ON DELETE CASCADE,
            tenant_id  INTEGER NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
            start_date TEXT NOT NULL,
            end_date   TEXT
        );
                         
        CREATE TABLE IF NOT EXISTS room_payment (
            room_id    INTEGER NOT NULL REFERENCES rooms(room_id) ON DELETE CASCADE,
            payment_id INTEGER NOT NULL REFERENCES payments(payment_id) ON DELETE CASCADE,
            PRIMARY KEY (room_id, payment_id)
        );
    """)

    conn.commit()
    conn.close()
