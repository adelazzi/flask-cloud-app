"""
routes/ui.py — Serves the student management web interface.
"""
from flask import Blueprint, render_template

ui_bp = Blueprint("ui", __name__)


@ui_bp.get("/students")
def students_page():
    return render_template("index.html")