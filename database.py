"""
database.py — all SQLite read/write lives here.

SQLite is a simple file-based database. Think of it as a spreadsheet
that Python can query. The file lives at data/spanish_trainer.db and
is created automatically the first time you run the app.
"""

import sqlite3
import os

# Path to the database file — stored in a 'data' subfolder
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'spanish_trainer.db')


def get_connection():
    """Open a connection (a 'line' to talk to the database)."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # makes rows behave like dicts
    return conn


def init_db():
    """Create the tables if they don't exist yet. Safe to call every startup."""
    conn = get_connection()
    conn.executescript('''
        -- cards: one row per flashcard
        CREATE TABLE IF NOT EXISTS cards (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt      TEXT    NOT NULL,           -- English side (what you see first)
            spanish     TEXT    NOT NULL,           -- Correct Spanish answer
            error_type  TEXT    NOT NULL,           -- Category (e.g. preterite_vs_imperfect)
            -- SM-2 scheduling fields (used in Phase 5):
            interval    INTEGER DEFAULT 1,          -- Days until next review
            repetitions INTEGER DEFAULT 0,          -- Consecutive correct answers so far
            ease_factor REAL    DEFAULT 2.5,        -- How easily you recall this card
            due_date    TEXT    DEFAULT (date('now')),  -- Next review date
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        -- review_log: one row every time you grade a card
        CREATE TABLE IF NOT EXISTS review_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id     INTEGER NOT NULL,
            reviewed_at TEXT    DEFAULT (datetime('now')),
            grade       TEXT    NOT NULL,   -- 'got_it', 'shaky', or 'missed_it'
            FOREIGN KEY (card_id) REFERENCES cards(id)
        );
    ''')
    conn.commit()
    conn.close()


# ── Card CRUD (Create, Read, Update, Delete) ──────────────────────────────────

def add_card(prompt, spanish, error_type):
    """Save one new flashcard to the database."""
    conn = get_connection()
    conn.execute(
        'INSERT INTO cards (prompt, spanish, error_type) VALUES (?, ?, ?)',
        (prompt, spanish, error_type)
    )
    conn.commit()
    conn.close()


def add_cards_bulk(card_list):
    """Save a list of card dicts at once. Each dict needs prompt/spanish/error_type."""
    conn = get_connection()
    conn.executemany(
        'INSERT INTO cards (prompt, spanish, error_type) VALUES (?, ?, ?)',
        [(c['prompt'], c['spanish'], c['error_type']) for c in card_list]
    )
    conn.commit()
    conn.close()


def get_all_cards():
    """Return every card, newest first."""
    conn = get_connection()
    rows = conn.execute('SELECT * FROM cards ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_due_cards():
    """Return cards whose review date is today or earlier."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM cards WHERE due_date <= date('now') ORDER BY due_date ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_card_schedule(card_id, interval, repetitions, ease_factor, due_date):
    """After a review, update the SM-2 scheduling fields for one card."""
    conn = get_connection()
    conn.execute(
        '''UPDATE cards
           SET interval=?, repetitions=?, ease_factor=?, due_date=?
           WHERE id=?''',
        (interval, repetitions, ease_factor, due_date, card_id)
    )
    conn.commit()
    conn.close()


def log_review(card_id, grade):
    """Record that you reviewed a card and what grade you gave it."""
    conn = get_connection()
    conn.execute(
        'INSERT INTO review_log (card_id, grade) VALUES (?, ?)',
        (card_id, grade)
    )
    conn.commit()
    conn.close()


def get_review_log_last_7_days():
    """Return all review events from the past 7 days, joined with card info."""
    conn = get_connection()
    rows = conn.execute('''
        SELECT r.reviewed_at, r.grade, c.error_type, c.prompt
        FROM review_log r
        JOIN cards c ON c.id = r.card_id
        WHERE r.reviewed_at >= datetime('now', '-7 days')
        ORDER BY r.reviewed_at DESC
    ''').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_streak():
    """
    Return the current daily review streak (number of consecutive days
    that had at least one review, counting back from today).
    """
    conn = get_connection()
    rows = conn.execute('''
        SELECT DISTINCT date(reviewed_at) AS review_date
        FROM review_log
        ORDER BY review_date DESC
    ''').fetchall()
    conn.close()

    from datetime import date, timedelta
    today = date.today()
    streak = 0
    for row in rows:
        expected = today - timedelta(days=streak)
        if row['review_date'] == str(expected):
            streak += 1
        else:
            break
    return streak
