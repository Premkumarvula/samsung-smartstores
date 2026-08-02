from flask import Blueprint, render_template, current_app
from sqlalchemy import text

from app.extensions import db
from app.models import Product

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    products = Product.query.filter_by(is_active=True).all()
    return render_template("index.html", products=products)


@main_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = db.get_or_404(Product, product_id)
    return render_template("product.html", product=product)


@main_bp.route("/health")
def health():
    """
    Liveness/readiness probe for load balancers, GitHub Actions deploy
    checks, and Dynatrace synthetic monitors. Verifies the DB connection
    too, so a broken database shows up as unhealthy instead of a silent 200.
    """
    db_status = "UP"
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - we want to report any DB failure
        current_app.logger.error("Health check DB failure: %s", exc)
        db_status = "DOWN"

    overall = "UP" if db_status == "UP" else "DOWN"
    status_code = 200 if overall == "UP" else 503

    return {
        "status": overall,
        "database": db_status,
        "service": "samsung-smartstore",
    }, status_code
