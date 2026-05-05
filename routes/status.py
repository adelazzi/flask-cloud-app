"""
routes/status.py — Root status endpoint.
GET / → returns app info + timestamp.
"""
from datetime import datetime, timezone

from flask import Blueprint, jsonify

status_bp = Blueprint("status", __name__)


@status_bp.get("/")
def index():
    return jsonify(
        {
            "app": "flask-cloud-app",
            "status": "running",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoints": ["/", "/health", "/mysql-test", "/mongo-test"],
        }
    )
