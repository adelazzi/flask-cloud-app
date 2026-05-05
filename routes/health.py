"""
routes/health.py — Aggregated health check endpoint.
GET /health → checks MySQL + MongoDB and returns combined status.

HTTP 200 if app is running (even if DBs are down — app itself is healthy).
HTTP 503 only if BOTH databases are unreachable (fully degraded).
"""
from flask import Blueprint, jsonify

from db import mongo, mysql

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    mysql_status = mysql.ping()
    mongo_status = mongo.ping()

    both_down = (
        mysql_status["status"] == "error"
        and mongo_status["status"] == "error"
    )

    payload = {
        "app": "ok",
        "mysql": mysql_status,
        "mongo": mongo_status,
    }

    http_status = 503 if both_down else 200
    return jsonify(payload), http_status
