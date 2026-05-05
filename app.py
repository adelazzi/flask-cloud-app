"""
app.py — Flask application factory + entry point.
"""
import logging
import sys

from flask import Flask

from config import config
from routes.db_tests import db_test_bp
from routes.health import health_bp
from routes.status import status_bp
from routes.students import students_bp
from routes.logs import logs_bp
from routes.ui import ui_bp


def create_app() -> Flask:
    app = Flask(__name__)

    logging.basicConfig(
        level=logging.DEBUG if config.FLASK_DEBUG else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )

    app.register_blueprint(status_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(db_test_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(ui_bp)
    from db.mysql import init_db

    # at the end of create_app(), before return app:
    with app.app_context():
        init_db()
    app.logger.info("Blueprints registered: status, health, db_tests, students, logs, ui.")
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.APP_PORT, debug=config.FLASK_DEBUG)