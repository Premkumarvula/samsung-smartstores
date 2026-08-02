"""
Standalone seeding script: `python seed.py`

Equivalent to `flask seed-db`, kept as a script too since that's how the
original project seeded data and some deploy pipelines may already call it.
"""
from app import create_app
from app.extensions import db
from app.seed_data import seed_products

app = create_app()

with app.app_context():
    db.create_all()
    seed_products()
