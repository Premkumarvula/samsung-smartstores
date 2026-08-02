"""
Logging setup.

- Console handler: picked up by Gunicorn/systemd/journald, which Dynatrace
  OneAgent's log monitoring reads from directly on EC2.
- Rotating file handler: keeps a local audit trail without unbounded disk
  growth on a small t3.micro instance (5 files x 2MB max).
Format includes timestamp, level, logger name, and message — enough
structure for Dynatrace log parsing rules without adding a JSON logging
dependency.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def configure_logging(app):
    log_dir = app.config.get("LOG_DIR")
    os.makedirs(log_dir, exist_ok=True)

    level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "smartstore.log"), maxBytes=2 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    app.logger.handlers.clear()
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(level)

    # Quiet down noisy SQLAlchemy engine logs unless explicitly debugging.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    app.logger.info("Logging configured (level=%s)", app.config.get("LOG_LEVEL"))
