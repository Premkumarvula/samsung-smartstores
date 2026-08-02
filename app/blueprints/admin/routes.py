from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Product, Order, User
from app.forms import ProductForm

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "product_count": Product.query.count(),
        "order_count": Order.query.count(),
        "user_count": User.query.count(),
        "revenue": db.session.query(db.func.coalesce(db.func.sum(Order.total), 0.0)).scalar(),
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template("admin/dashboard.html", stats=stats, recent_orders=recent_orders)


@admin_bp.route("/products")
@login_required
@admin_required
def product_list():
    products = Product.query.order_by(Product.id).all()
    return render_template("admin/products.html", products=products)


@admin_bp.route("/products/new", methods=["GET", "POST"])
@login_required
@admin_required
def product_new():
    form = ProductForm()

    if form.validate_on_submit():
        product = Product(
            name=form.name.data.strip(),
            price=form.price.data,
            description=form.description.data,
            image=form.image.data or "placeholder.jpg",
            stock=form.stock.data,
        )
        db.session.add(product)
        db.session.commit()
        current_app.logger.info("Admin %s created product #%s", current_user.email, product.id)
        flash(f"Product '{product.name}' created.", "success")
        return redirect(url_for("admin.product_list"))

    return render_template("admin/product_form.html", form=form, title="New Product")


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def product_edit(product_id):
    product = db.get_or_404(Product, product_id)
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        form.populate_obj(product)
        db.session.commit()
        current_app.logger.info("Admin %s updated product #%s", current_user.email, product.id)
        flash(f"Product '{product.name}' updated.", "success")
        return redirect(url_for("admin.product_list"))

    return render_template("admin/product_form.html", form=form, title="Edit Product")


@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
@admin_required
def product_delete(product_id):
    product = db.get_or_404(Product, product_id)
    product.is_active = False  # soft delete: preserves order history integrity
    db.session.commit()
    current_app.logger.info("Admin %s deactivated product #%s", current_user.email, product.id)
    flash(f"Product '{product.name}' deactivated.", "success")
    return redirect(url_for("admin.product_list"))
