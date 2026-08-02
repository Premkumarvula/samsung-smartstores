from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Product, Order, OrderItem

cart_bp = Blueprint("cart", __name__)


def _get_cart():
    """Cart is a dict of {product_id (str): quantity} stored in the session.

    Kept intentionally simple (no Redis / DB-backed cart) since the app
    must run comfortably on a t3.micro instance and carts are short-lived.
    """
    return session.get("cart", {})


def _save_cart(cart):
    session["cart"] = cart
    session.modified = True


@cart_bp.route("/cart")
def view_cart():
    cart = _get_cart()
    items = []
    total = 0.0

    if cart:
        products = Product.query.filter(Product.id.in_([int(pid) for pid in cart])).all()
        products_by_id = {p.id: p for p in products}

        for pid_str, qty in cart.items():
            product = products_by_id.get(int(pid_str))
            if not product:
                continue  # product may have been deleted since it was added
            subtotal = round(product.price * qty, 2)
            total += subtotal
            items.append({"product": product, "quantity": qty, "subtotal": subtotal})

    return render_template("cart.html", items=items, total=round(total, 2))


@cart_bp.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = db.get_or_404(Product, product_id)

    cart = _get_cart()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    _save_cart(cart)

    flash(f"{product.name} added to cart.", "success")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/cart/update/<int:product_id>", methods=["POST"])
def update_quantity(product_id):
    from flask import request

    cart = _get_cart()
    key = str(product_id)

    try:
        quantity = int(request.form.get("quantity", 1))
    except ValueError:
        quantity = 1

    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity

    _save_cart(cart)
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = _get_cart()
    cart.pop(str(product_id), None)
    _save_cart(cart)

    flash("Item removed from cart.", "success")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/cart/checkout", methods=["POST"])
@login_required
def checkout():
    cart = _get_cart()

    if not cart:
        flash("Your cart is empty.", "error")
        return redirect(url_for("cart.view_cart"))

    products = Product.query.filter(Product.id.in_([int(pid) for pid in cart])).all()
    products_by_id = {p.id: p for p in products}

    order = Order(user_id=current_user.id, status="PLACED", total=0.0)
    total = 0.0

    for pid_str, qty in cart.items():
        product = products_by_id.get(int(pid_str))
        if not product:
            continue
        order.items.append(
            OrderItem(product_id=product.id, quantity=qty, price_at_purchase=product.price)
        )
        total += product.price * qty

    order.total = round(total, 2)
    db.session.add(order)
    db.session.commit()

    session.pop("cart", None)
    current_app.logger.info("Order #%s placed by user %s (total=%s)", order.id, current_user.email, order.total)

    flash(f"Order #{order.id} placed successfully!", "success")
    return redirect(url_for("orders.order_detail", order_id=order.id))
