"""
Environment-driven configuration.

Never hardcode secrets in source. In production these values come from
environment variables set on the EC2 instance (or a `.env` file loaded by
python-dotenv in development).
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Load a local .env file in development only (harmless no-op if missing / in prod).
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "store.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Session / cookie hardening
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7  # 7 days

    WTF_CSRF_ENABLED = True

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_DIR = os.environ.get("LOG_DIR", os.path.join(BASE_DIR, "logs"))


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    # Requires HTTPS (terminated at Nginx) — cookies only sent over TLS.
    SESSION_COOKIE_SECURE = True

    @staticmethod
    def validate():
        """Fail fast on startup if a required prod secret is missing/insecure."""
        secret = os.environ.get("SECRET_KEY")
        if not secret or secret == "dev-only-insecure-key-change-me":
            raise RuntimeError(
                "SECRET_KEY environment variable must be set to a strong random "
                "value in production."
            )


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


_CONFIGS = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(name=None):
    name = name or os.environ.get("FLASK_ENV", "development")
    config_cls = _CONFIGS.get(name, DevelopmentConfig)
    if config_cls is ProductionConfig:
        config_cls.validate()
    return config_cls
