"""Persistent human decisions; local SQLite only."""
import sqlite3
from datetime import datetime, timezone

def connect(path="trade_lab.sqlite3"):
    con = sqlite3.connect(path)
    con.execute("""CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT, created_utc TEXT NOT NULL,
        evidence_sha256 TEXT NOT NULL, ai_output_sha256 TEXT NOT NULL,
        decision TEXT NOT NULL, reviewer TEXT NOT NULL, notes TEXT NOT NULL
    )""")
    con.commit()
    return con

def add_review(con, evidence_sha256, ai_output_sha256, decision, reviewer, notes):
    if decision not in ("approved", "rejected", "needs_revision"):
        raise ValueError("Invalid review decision")
    if not reviewer.strip():
        raise ValueError("Reviewer is required")
    con.execute("INSERT INTO reviews (created_utc,evidence_sha256,ai_output_sha256,decision,reviewer,notes) VALUES (?,?,?,?,?,?)", (datetime.now(timezone.utc).isoformat(),evidence_sha256,ai_output_sha256,decision,reviewer.strip(),notes))
    con.commit()

def list_reviews(con):
    return con.execute("SELECT id,created_utc,evidence_sha256,ai_output_sha256,decision,reviewer,notes FROM reviews ORDER BY id DESC").fetchall()
