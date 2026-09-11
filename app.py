from flask import Flask, render_template, session, redirect, url_for, request

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "rich-secret-key"


# إعداد قاعدة البيانات
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///rich.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# Products
# =========================

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(300), nullable=True)

    category = db.Column(db.String(50), nullable=True)

    stock = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# Bundles
# =========================

class Bundle(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(300), nullable=True)

    stock = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# Orders
# =========================

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=False)

    city = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(300), nullable=True)

    total = db.Column(db.Float, nullable=False)

    status = db.Column(
        db.String(50),
        default="جديد"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================
# Gift Options
# =========================

class GiftOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    recipient_name = db.Column(db.String(150), nullable=True)
    recipient_phone = db.Column(db.String(50), nullable=True)

    occasion = db.Column(db.String(100), nullable=True)

    message = db.Column(db.Text, nullable=True)

    gift_wrapping = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
 # =========================
# Add test product
# =========================

with app.app_context():

    if Product.query.count() == 0:

        test_product = Product(
            name="RICH Noir",
            description="عطر أنيق بلمسة فاخرة ومميزة.",
            price=25.0,
            image="noir.jpg",
            category="رجالي",
            stock=20
        )

        db.session.add(test_product)
        db.session.commit()

        print("Test product added successfully!")



# =========================
# Pages
# =========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/products")
def products():
    products = Product.query.all()

    return render_template(
        "products.html",
        products=products
    )

@app.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)

    return render_template(
        "product.html",
        product=product
    )
@app.route("/add-to-cart/<int:product_id>", methods=["GET", "POST"])
def add_to_cart(product_id):

    product = Product.query.get_or_404(product_id)

    cart = session.get("cart", {})

    product_id = str(product.id)

    # الكمية التي اختارها الزبون
    if request.method == "POST":
        try:
            quantity = int(request.form.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 1
    else:
        quantity = 1

    # منع الكميات غير الصحيحة
    if quantity < 1:
        quantity = 1

    # منع طلب كمية أكبر من المخزون
    if quantity > product.stock:
        quantity = product.stock

    # إضافة الكمية للسلة
    cart[product_id] = quantity


    session["cart"] = cart

    return redirect(url_for("cart"))





@app.route("/bundles")
def bundles():
    bundles = Bundle.query.all()

    return render_template(
        "bundles.html",
        bundles=bundles
    )


@app.route("/gifts")
def gifts():
    return render_template("gifts.html")


@app.route("/cart")
def cart():

    cart = session.get("cart", {})

    cart_items = []
    total = 0

    for product_id, quantity in cart.items():

        product = Product.query.get(int(product_id))

        if product:

            subtotal = product.price * quantity

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

            total += subtotal

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )



@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    cart = session.get("cart", {})

    if not cart:
        return redirect(url_for("products"))

    total = 0

    for product_id, quantity in cart.items():

        product = Product.query.get(int(product_id))

        if product:
            total += product.price * quantity

    if request.method == "POST":

        customer_name = request.form.get("customer_name")
        phone = request.form.get("phone")
        city = request.form.get("city")
        address = request.form.get("address")

        order = Order(
            customer_name=customer_name,
            phone=phone,
            city=city,
            address=address,
            total=total
        )

        db.session.add(order)
        db.session.commit()

        session["cart"] = {}

        return render_template(
            "order_success.html",
            order=order
        )

    return render_template(
        "checkout.html",
        total=total
    )



@app.route("/admin")
def admin():

    orders = Order.query.order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "admin.html",
        orders=orders
    )
@app.route("/admin/order/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):

    order = Order.query.get_or_404(order_id)

    new_status = request.form.get("status")

    order.status = new_status

    db.session.commit()

    return redirect(url_for("admin"))




# =========================
# Create Database
# =========================

with app.app_context():
    db.create_all()


# =========================
# Run
# =========================

if __name__ == "__main__":
    app.run(debug=True)
