"""
db/mysql.py — MySQL connection helper (non-blocking, per-request).

Design decisions:
  - No module-level connection pool that blocks startup.
  - get_connection() is called only inside request handlers.
  - connect_timeout is short so failures are fast, not hanging.
"""
import logging

import pymysql
import pymysql.cursors

from config import config

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT = 3  # seconds — fail fast, don't hang the request


def get_connection() -> pymysql.Connection:
    """
    Open and return a raw PyMySQL connection.
    Caller is responsible for closing it (use as context manager).
    Raises pymysql.Error on failure — callers must handle this.
    """
    return pymysql.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
        connect_timeout=CONNECT_TIMEOUT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def ping() -> dict:
    """
    Attempt a lightweight connection check.
    Returns a status dict — never raises.
    """
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT VERSION() AS version")
                row = cur.fetchone()
        return {"status": "ok", "version": row["version"]}
    except pymysql.Error as exc:
        logger.warning("MySQL ping failed: %s", exc)
        return {"status": "error", "detail": str(exc)}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected MySQL error")
        return {"status": "error", "detail": str(exc)}


def run_query(sql: str, args: tuple = ()) -> list[dict]:
    """
    Execute a SELECT query and return rows as a list of dicts.
    Raises on error — wrap in try/except in the route.
    """
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchall()
