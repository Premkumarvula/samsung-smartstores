from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager
from app.models import User
from app.forms import RegisterForm, LoginForm

auth_bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return redirect(url_for("auth.register"))

        user = User(
            username=form.username.data.strip(),
            email=email,
            password_hash=generate_password_hash(form.password.data),
        )
        db.session.add(user)
        db.session.commit()

        current_app.logger.info("New user registered: %s", email)
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            current_app.logger.info("User logged in: %s", email)
            flash("Login successful!", "success")

            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.home"))

        current_app.logger.warning("Failed login attempt for: %s", email)
        flash("Invalid email or password.", "error")

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    current_app.logger.info("User logged out: %s", current_user.email)
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("main.home"))
