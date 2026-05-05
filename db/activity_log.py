"""
db/activity_log.py — MongoDB-backed audit log.

Every student create / update / delete writes a document here.
This is a classic hybrid pattern: MySQL for structured relational data,
MongoDB for flexible, append-only event/audit logs.
"""
import logging
from datetime import datetime, timezone

from pymongo.errors import PyMongoError

from db.mongo import get_db

logger = logging.getLogger(__name__)

COLLECTION = "activity_logs"


def _col():
    return get_db()[COLLECTION]


def log_action(action: str, student: dict) -> None:
    """
    Write an audit log entry. Fails silently so a Mongo outage
    never breaks the main student API.

    action: 'created' | 'updated' | 'deleted'
    student: dict with at least id, name, family_name, matricule, mark
    """
    try:
        doc = {
            "action":       action,
            "student_id":   student.get("id"),
            "student_name": f"{student.get('name','')} {student.get('family_name','')}".strip(),
            "matricule":    student.get("matricule"),
            "mark":         student.get("mark"),
            "status":       "success" if float(student.get("mark", 0)) >= 10 else "failed",
            "timestamp":    datetime.now(timezone.utc),
        }
        _col().insert_one(doc)
    except PyMongoError as exc:
        logger.warning("activity_log: could not write log — %s", exc)
    except Exception as exc:  # noqa: BLE001
        logger.warning("activity_log: unexpected error — %s", exc)


def get_logs(limit: int = 100) -> list[dict]:
    """Return the most recent `limit` log entries, newest first."""
    try:
        docs = list(
            _col()
            .find({}, {"_id": 0})
            .sort("timestamp", -1)
            .limit(limit)
        )
        # Convert datetime to ISO string for JSON serialisation
        for doc in docs:
            if isinstance(doc.get("timestamp"), datetime):
                doc["timestamp"] = doc["timestamp"].isoformat()
        return docs
    except PyMongoError as exc:
        logger.warning("activity_log: could not read logs — %s", exc)
        return []