"""
db/mongo.py — MongoDB connection helper (non-blocking, per-request).

Design decisions:
  - MongoClient is lazily created and cached at module level (thread-safe).
  - serverSelectionTimeoutMS is short so unavailability is caught fast.
  - ping() uses the admin command — works even on empty databases.
"""
import logging
from threading import Lock
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import config

logger = logging.getLogger(__name__)

SERVER_SELECTION_TIMEOUT_MS = 3_000  # 3 seconds

_client: Optional[MongoClient] = None
_client_lock = Lock()


def get_client() -> MongoClient:
    """
    Return a cached MongoClient, creating it lazily on first call.
    MongoClient itself is non-blocking at creation time — the timeout
    only fires when an actual operation is attempted.
    """
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:  # double-checked locking
                _client = MongoClient(
                    config.MONGO_URI,
                    serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT_MS,
                    connectTimeoutMS=SERVER_SELECTION_TIMEOUT_MS,
                    socketTimeoutMS=SERVER_SELECTION_TIMEOUT_MS,
                )
    return _client


def get_db():
    """Return the configured database handle."""
    return get_client()[config.MONGO_DATABASE]


def ping() -> dict:
    """
    Attempt a lightweight server ping.
    Returns a status dict — never raises.
    """
    try:
        client = get_client()
        result = client.admin.command("ping")
        return {"status": "ok", "ping_response": result}
    except PyMongoError as exc:
        logger.warning("MongoDB ping failed: %s", exc)
        return {"status": "error", "detail": str(exc)}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected MongoDB error")
        return {"status": "error", "detail": str(exc)}
