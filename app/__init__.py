"""
Application factory for Samsung SmartStore.

Using the factory pattern (instead of a single global `app.py`) keeps the
codebase modular and testable: each blueprint owns its own routes, and
extensions (db, csrf, login manager) are initialized once here and shared.
"""
import os

from flask import Flask, render_template

from app.config import get_config
from app.extensions import db, csrf, login_manager
from app.logging_config import configure_logging


def create_app(config_name=None):
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
    )

    app.config.from_object(get_config(config_name))

    configure_logging(app)

    # ---- Extensions ----
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to continue."
    login_manager.login_message_category = "info"

    # ---- Blueprints ----
    from app.blueprints.main.routes import main_bp
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.cart.routes import cart_bp
    from app.blueprints.orders.routes import orders_bp
    from app.blueprints.admin.routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)

    register_error_handlers(app)
    register_cli_commands(app)

    @app.context_processor
    def inject_cart_count():
        """Make the cart item count available to every template (nav badge)."""
        from flask import session
        cart = session.get("cart", {})
        return {"cart_count": sum(cart.values()) if cart else 0}

    return app


def register_error_handlers(app):
    """Custom error pages so users (and Dynatrace) never see a raw traceback."""

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception("Unhandled server error: %s", error)
        return render_template("errors/500.html"), 500

    @app.errorhandler(400)
    def bad_request(error):
        return render_template("errors/400.html"), 400


def register_cli_commands(app):
    """`flask seed-db` — seed sample product data without a separate script call."""

    @app.cli.command("seed-db")
    def seed_db():
        from app.seed_data import seed_products
        seed_products()
        print("Database seeded.")

    @app.cli.command("create-admin")
    def create_admin():
        """flask create-admin — interactive helper to promote/create an admin user."""
        from app.models import User
        from app.extensions import db as _db
        from werkzeug.security import generate_password_hash

        username = input("Admin username: ").strip()
        email = input("Admin email: ").strip().lower()
        password = input("Admin password: ").strip()

        user = User.query.filter_by(email=email).first()
        if user:
            user.is_admin = True
            print(f"Existing user {email} promoted to admin.")
        else:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                is_admin=True,
            )
            _db.session.add(user)
            print(f"New admin user {email} created.")

        _db.session.commit()
