"""
Gunicorn entrypoint: `gunicorn -c gunicorn.conf.py wsgi:app`

Kept separate from `app/__init__.py` so the app factory stays reusable
(tests, CLI commands, dev server) without importing a production-only entry
point.
"""
import os

from app import create_app
from app.extensions import db

app = create_app(os.environ.get("FLASK_ENV", "production"))

# Ensure tables exist on first boot. In a mature production setup this would
# be replaced by Alembic migrations (flask-migrate) run as a separate
# deploy step, but for this project's scope create_all() is sufficient and
# keeps the dependency footprint small.
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
