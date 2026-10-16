"""
SQLite Database module for QR Code Generator History and Analytics
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "qr_history.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the history table if it doesn't already exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS qr_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qr_type TEXT NOT NULL,
                label TEXT NOT NULL,
                payload TEXT NOT NULL,
                image_blob BLOB NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_qr(qr_type: str, label: str, payload: str, image_blob: bytes) -> int:
    """Save a generated QR code into the database and return its new ID."""
    init_db()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO qr_history (qr_type, label, payload, image_blob, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (qr_type, label, payload, image_blob, now_str),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_qrs() -> List[Dict[str, Any]]:
    """Retrieve all saved QR codes ordered newest to oldest."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, qr_type, label, payload, image_blob, created_at
            FROM qr_history
            ORDER BY id DESC
            """
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_qr_by_id(qr_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single QR code record by ID."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, qr_type, label, payload, image_blob, created_at
            FROM qr_history
            WHERE id = ?
            """,
            (qr_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_qr(qr_id: int) -> bool:
    """Delete a saved QR code record by ID."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM qr_history WHERE id = ?", (qr_id,))
        conn.commit()
        return cursor.rowcount > 0


def clear_all_history() -> bool:
    """Clear all saved QR history."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM qr_history")
        conn.commit()
        return True


def get_qr_stats() -> Dict[str, Any]:
    """Get total count and breakdown by QR type."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM qr_history")
        total = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT qr_type, COUNT(*) as count
            FROM qr_history
            GROUP BY qr_type
            ORDER BY count DESC
            """
        )
        by_type = {row["qr_type"]: row["count"] for row in cursor.fetchall()}
        return {"total": total, "by_type": by_type}
