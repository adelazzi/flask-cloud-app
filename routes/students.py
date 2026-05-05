"""
routes/students.py — Full CRUD REST API for students.

Every write operation logs an audit entry to MongoDB via activity_log.
"""
import re
import logging

from flask import Blueprint, jsonify, request
import pymysql

from db.mysql import get_connection
from db.activity_log import log_action

logger = logging.getLogger(__name__)
students_bp = Blueprint("students", __name__, url_prefix="/api/students")

MATRICULE_RE = re.compile(r"^\d{12}$")


def validate_payload(data: dict, require_all: bool = True) -> list[str]:
    errors = []
    if require_all or "matricule" in data:
        m = data.get("matricule", "")
        if not MATRICULE_RE.match(str(m)):
            errors.append("matricule must be exactly 12 digits")
    if require_all or "name" in data:
        if not str(data.get("name", "")).strip():
            errors.append("name is required")
    if require_all or "family_name" in data:
        if not str(data.get("family_name", "")).strip():
            errors.append("family_name is required")
    if require_all or "mark" in data:
        try:
            mark = float(data.get("mark", -1))
            if not (0 <= mark <= 20):
                raise ValueError
        except (TypeError, ValueError):
            errors.append("mark must be a number between 0 and 20")
    return errors


def row_to_dict(row: dict) -> dict:
    mark = float(row["mark"])
    return {
        "id":          row["id"],
        "matricule":   row["matricule"],
        "name":        row["name"],
        "family_name": row["family_name"],
        "mark":        mark,
        "status":      "success" if mark >= 10 else "failed",
        "created_at":  str(row["created_at"]),
        "updated_at":  str(row["updated_at"]),
    }


@students_bp.get("/")
def list_students():
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM students ORDER BY created_at DESC")
                rows = cur.fetchall()
        return jsonify([row_to_dict(r) for r in rows])
    except pymysql.Error as e:
        logger.error("list_students: %s", e)
        return jsonify({"error": str(e)}), 503


@students_bp.post("/")
def create_student():
    data = request.get_json(silent=True) or {}
    errors = validate_payload(data, require_all=True)
    if errors:
        return jsonify({"errors": errors}), 400
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO students (matricule, name, family_name, mark) VALUES (%s, %s, %s, %s)",
                    (data["matricule"], data["name"].strip(),
                     data["family_name"].strip(), float(data["mark"])),
                )
                new_id = cur.lastrowid
                cur.execute("SELECT * FROM students WHERE id = %s", (new_id,))
                row = cur.fetchone()
        result = row_to_dict(row)
        log_action("created", result)
        return jsonify(result), 201
    except pymysql.IntegrityError:
        return jsonify({"error": "matricule already exists"}), 409
    except pymysql.Error as e:
        logger.error("create_student: %s", e)
        return jsonify({"error": str(e)}), 503


@students_bp.get("/<int:student_id>")
def get_student(student_id: int):
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
                row = cur.fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(row_to_dict(row))
    except pymysql.Error as e:
        logger.error("get_student: %s", e)
        return jsonify({"error": str(e)}), 503


@students_bp.put("/<int:student_id>")
def update_student(student_id: int):
    data = request.get_json(silent=True) or {}
    errors = validate_payload(data, require_all=False)
    if errors:
        return jsonify({"errors": errors}), 400

    fields, values = [], []
    for col in ("matricule", "name", "family_name"):
        if col in data:
            fields.append(f"{col} = %s")
            values.append(data[col].strip() if col != "matricule" else data[col])
    if "mark" in data:
        fields.append("mark = %s")
        values.append(float(data["mark"]))
    if not fields:
        return jsonify({"error": "no fields to update"}), 400

    values.append(student_id)
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE students SET {', '.join(fields)} WHERE id = %s",
                    values,
                )
                if cur.rowcount == 0:
                    return jsonify({"error": "not found"}), 404
                cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
                row = cur.fetchone()
        result = row_to_dict(row)
        log_action("updated", result)
        return jsonify(result)
    except pymysql.IntegrityError:
        return jsonify({"error": "matricule already exists"}), 409
    except pymysql.Error as e:
        logger.error("update_student: %s", e)
        return jsonify({"error": str(e)}), 503


@students_bp.delete("/<int:student_id>")
def delete_student(student_id: int):
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM students WHERE id = %s", (student_id,))
                row = cur.fetchone()
                if not row:
                    return jsonify({"error": "not found"}), 404
                cur.execute("DELETE FROM students WHERE id = %s", (student_id,))
        log_action("deleted", row_to_dict(row))
        return jsonify({"deleted": student_id})
    except pymysql.Error as e:
        logger.error("delete_student: %s", e)
        return jsonify({"error": str(e)}), 503