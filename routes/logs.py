"""
routes/logs.py — Activity log endpoints.

GET /api/logs          → returns last 100 audit log entries from MongoDB
GET /logs              → serves the logs web UI page
"""
from flask import Blueprint, jsonify, render_template
from db.activity_log import get_logs

logs_bp = Blueprint("logs", __name__)


@logs_bp.get("/api/logs")
def api_logs():
    return jsonify(get_logs(limit=100))


@logs_bp.get("/logs")
def logs_page():
    return render_template("logs.html")