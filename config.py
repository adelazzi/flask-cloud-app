"""
config.py — Centralised environment variable loading.
All other modules import from here; nothing reads os.environ directly.
"""
import os


class Config:
    # ── Flask ─────────────────────────────────────────────────────────────
    FLASK_ENV: str = os.getenv("FLASK_ENV", "production")
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "0") == "1"
    APP_PORT: int = int(os.getenv("APP_PORT", "5000"))

    # ── MySQL ─────────────────────────────────────────────────────────────
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "appuser")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "appdb")

    # ── MongoDB ───────────────────────────────────────────────────────────
    MONGO_HOST: str = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT", "27017"))
    MONGO_USER: str = os.getenv("MONGO_USER", "appuser")
    MONGO_PASSWORD: str = os.getenv("MONGO_PASSWORD", "")
    MONGO_DATABASE: str = os.getenv("MONGO_DATABASE", "appdb")

    @property
    def MYSQL_URI(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    @property
    def MONGO_URI(self) -> str:
        return (
            f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}"
            f"@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DATABASE}"
            "?authSource=admin"
        )


# Singleton — import this everywhere
config = Config()
