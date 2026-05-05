"""
routes/db_tests.py — Individual database test endpoints.

GET /mysql-test → runs a real SELECT query against MySQL.
GET /mongo-test → inserts + retrieves a document from MongoDB.

Both return clean JSON on success AND on failure (never crash the app).
"""
import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify
from pymongo.errors import PyMongoError
import pymysql

from db import mongo, mysql

logger = logging.getLogger(__name__)
db_test_bp = Blueprint("db_tests", __name__)


# ── MySQL Test ─────────────────────────────────────────────────────────────

@db_test_bp.get("/mysql-test")
def mysql_test():
    try:
        rows = mysql.run_query(
            "SELECT 'hello from MySQL' AS message, NOW() AS server_time"
        )
        return jsonify({"status": "ok", "result": rows})
    except pymysql.Error as exc:
        logger.warning("MySQL test failed: %s", exc)
        return jsonify({"status": "error", "detail": str(exc)}), 503
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error in /mysql-test")
        return jsonify({"status": "error", "detail": str(exc)}), 500


# ── MongoDB Test ───────────────────────────────────────────────────────────

@db_test_bp.get("/mongo-test")
def mongo_test():
    try:
        db = mongo.get_db()
        collection = db["health_checks"]

        doc = {
            "message": "hello from MongoDB",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        result = collection.insert_one(doc)

        # Fetch the document we just inserted (proves read works too)
        saved = collection.find_one(
            {"_id": result.inserted_id},
            {"_id": 0},  # exclude Mongo internal _id from response
        )

        return jsonify({"status": "ok", "inserted": saved})
    except PyMongoError as exc:
        logger.warning("MongoDB test failed: %s", exc)
        return jsonify({"status": "error", "detail": str(exc)}), 503
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error in /mongo-test")
        return jsonify({"status": "error", "detail": str(exc)}), 500
