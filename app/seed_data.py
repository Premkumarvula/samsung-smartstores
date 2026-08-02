from app.extensions import db
from app.models import Product


def seed_products():

    if Product.query.count() > 0:
        print("Products already exist.")
        return

    products = [

        Product(
            name="Galaxy S26 Ultra",
            price=1299,
            description="Samsung flagship smartphone with Galaxy AI and advanced camera.",
            image="phone.jpg"
        ),

        Product(
            name="Galaxy Watch 9",
            price=399,
            description="Premium smartwatch with advanced health tracking.",
            image="watch.png"
        ),

        Product(
            name="Galaxy Buds Pro",
            price=249,
            description="Noise cancelling wireless earbuds.",
            image="buds.jpg"
        ),

        Product(
            name="Neo QLED TV",
            price=2499,
            description="75-inch Samsung Neo QLED 4K Smart TV.",
            image="tv.webp"
        )

    ]

    db.session.add_all(products)
    db.session.commit()

    print("Seeded 4 products.")