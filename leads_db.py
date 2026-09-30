"""
SQLite storage for community-reported penny/clearance leads. Kept in its
own DB (penny_leads.db), separate from Penny3's hd_clearance_history.db,
so the two discovery methods -- our own category-crawl vs. community
reports -- can be compared side by side rather than merged.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "penny_leads.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,          -- 'slickdeals' or 'reddit'
    thread_url TEXT NOT NULL,
    author TEXT,
    posted_at TEXT,                -- raw timestamp as shown on the site, not parsed/normalized
    text TEXT NOT NULL,
    scraped_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(source, thread_url, author, posted_at, text)
)
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    return conn


def insert_lead(
    conn: sqlite3.Connection,
    source: str,
    thread_url: str,
    author: str | None,
    posted_at: str | None,
    text: str,
) -> bool:
    """Returns True if a new row was inserted, False if this exact lead
    (same source/thread/author/timestamp/text) was already recorded --
    running the collector repeatedly against the same threads is meant to
    be a no-op for anything already seen."""
    cur = conn.execute(
        """
        INSERT OR IGNORE INTO leads (source, thread_url, author, posted_at, text)
        VALUES (?, ?, ?, ?, ?)
        """,
        (source, thread_url, author, posted_at, text),
    )
    conn.commit()
    return cur.rowcount > 0
