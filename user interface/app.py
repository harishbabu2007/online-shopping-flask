from flask import Flask, render_template, redirect, request, session, url_for, flash
from datetime import timedelta
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import flask_whooshalchemy as wa

app = Flask(__name__)
app.secret_key = "@$#^$%^$%*&DBG%^^$$%^$%^$%^$%$GFGJHJTYJTYHNT"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///db.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["WHOOSH_BASE"] = "whoosh_search"
app.permanent_session_lifetime = timedelta(days=365)
api = Api(app)

db = SQLAlchemy(app)

class Users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    email = db.Column("email", db.String(100), nullable=False)
    password = db.Column("password", db.String(100), nullable=False)
    cart = db.Column("cart", db.Integer, default=0)

    def __init__(self, name, email, password, cart):
        self.name = name
        self.email = email
        self.password = password
        self.cart = cart

class Products(db.Model):
    __searchable__ = ["name", "company", "search_terms"]

    name = db.Column("name", db.String(100), nullable=False)
    picture = db.Column("picture", db.String(1000), nullable=False)
    product_id = db.Column("product_id", db.Integer, primary_key=True)
    price = db.Column("price", db.Integer, nullable=False)
    stock = db.Column("stock", db.Integer, nullable=False)
    company = db.Column("company", db.String(100), nullable=False)
    search_terms = db.Column("search_terms", db.String(1000), nullable=True)
    description = db.Column("description", db.String(1000), nullable=False)
    pucrhases = db.Column("purchases", db.Integer)
    category = db.Column("category", db.String(100), nullable=False)

    def __init__(self, name, product_id, price, stock, company, search_terms, description, picture, category):
        self.name = name
        self.picture = picture
        self.product_id = product_id
        self.price = price
        self.stock = stock
        self.company = company
        self.search_terms = search_terms
        self.description = description
        self.category = category

class cart(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    picture = db.Column("picture", db.String(1000), nullable=False)
    product_id = db.Column("product_id", db.Integer, nullable=False)
    price = db.Column("price", db.Integer, nullable=False)
    email = db.Column("email", db.String(100), nullable=False)

    def __init__(self, name, picture, product_id, price, email):
        self.name = name
        self.picture = picture
        self.product_id = product_id
        self.price = price
        self.email = email

class Purchased(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    picture = db.Column("picture", db.String(1000), nullable=False)
    product_id = db.Column("product_id", db.Integer, nullable=False)
    price = db.Column("price", db.Integer, nullable=False)
    email = db.Column("email", db.String(100), nullable=False)

    def __init__(self, name, picture, product_id, price, email):
        self.name = name
        self.picture = picture
        self.product_id = product_id
        self.price = price
        self.email = email


wa.whoosh_index(app, Products)

getorder_add_args = reqparse.RequestParser()
getorder_add_args.add_argument("name", type=str, help="Nah")
getorder_add_args.add_argument("picture", type=str, help="Nah")
getorder_add_args.add_argument("product_id", type=int, help="Nah")
getorder_add_args.add_argument("price", type=int, help="Nah")
getorder_add_args.add_argument("stock", type=int, help="Nah")
getorder_add_args.add_argument("company", type=str, help="Nah")
getorder_add_args.add_argument("search_terms", type=str, help="Nah")
getorder_add_args.add_argument("description", type=str, help="Nah")
getorder_add_args.add_argument("category", type=str, help="Nah")

get_update_args = reqparse.RequestParser()
get_update_args.add_argument("product_id", type=int, help="Nah")
get_update_args.add_argument("price", type=int, help="Nah")
get_update_args.add_argument("stock", type=int, help="Nah")

delete_product_args = reqparse.RequestParser()
delete_product_args.add_argument("product_id", type=int, help="Nah")

resource_fields = {
	"name": fields.String,
    "product_id": fields.Integer,
    "price": fields.Integer,
    "stock": fields.Integer,
    "company": fields.String,
    "search_terms": fields.String,
    "description": fields.String,
    "category": fields.String
}

class GetOrders(Resource):
    @marshal_with(resource_fields)
    def put(self, order_id):
        args = getorder_add_args.parse_args()
        found_id = Products.query.filter_by(product_id=order_id).first()
        if found_id:
            abort(409, message="product id already exists")
            
        order = Products(
            name = args["name"],
            product_id= args["product_id"],
            price = args["price"],
            stock = args["stock"],
            company = args["company"],
            search_terms = args["search_terms"],
            description = args["description"],
            picture = args["picture"],
            category = args["category"]
        )
        db.session.add(order)
        db.session.commit()
        return order, 201

class update_stock(Resource):
    @marshal_with(resource_fields)
    def patch(self, order_id):
        args = get_update_args.parse_args()
        found_id = Products.query.filter_by(product_id=order_id).first()

        if not found_id:
            abort(409, message="invalid product id")

        if "stock" in args and args["stock"] != "":
            found_id.stock = args["stock"]
            db.session.commit()

        return found_id

class delete_product(Resource):
    @marshal_with(resource_fields)
    def delete(self, order_id):
        found_id = Products.query.filter_by(product_id=order_id).delete()

        if not found_id:
            abort(409, message="invalid product id")
        
        db.delete(table=Products)
        db.session.commit()

        return "Success"


api.add_resource(GetOrders, "/apifororders/getorders/<int:order_id>")
api.add_resource(delete_product, "/apifororders/deleteproduct/<int:order_id>")
api.add_resource(update_stock, "/apifororders/updatestock/<int:order_id>")


@app.route("/")
def index():
    if "user" in session:
        return render_template("signhome.html", user=session["user"], values=Products.query.all(), cart=Users.query.filter_by(email=session["email"]).first())
    else:
        return render_template("nonsignhome.html", values=Products.query.all())


@app.route("/search")
def search():
    query = request.args.get("query")
    if "user" in session:
        cart_cart = Users.query.filter_by(email=session["email"]).first()
        return render_template("signhome.html",cart=cart_cart, user=session["user"], values=Products.query.whoosh_search(query).all())
    else:
        return render_template("nonsignhome.html", values=Products.query.whoosh_search(query).all())


@app.route("/signin", methods=["POST", "GET"])
def signin():
    if request.method == "POST":
        session.permanent = True
        emailf = request.form["email"]
        password = request.form["password"]
        found_email = Users.query.filter_by(email=emailf).first()

        if found_email:
            if found_email.password == password:
                session["user"] = found_email.name
                session["email"] = emailf
                return redirect(url_for("index"))
            else:
                flash("Incorrect password")
                return redirect(url_for("signin"))
        else:
            flash("Email Not found")
            return redirect(url_for("signin"))

    return render_template("signin.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        session.permanent = True
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        found_email = Users.query.filter_by(email=email).first()

        if found_email:
            flash("Account with the same email already exists")
            return redirect(url_for("signup"))
        else:
            data = Users(name, email, password, cart=0)
            db.session.add(data)
            db.session.commit()

            session["user"] = name
            session["email"] = email 
            return redirect(url_for("index"))

    return render_template("signup.html")


@app.route("/product/<int:product_id>", methods=["POST", "GET"])
def product_show(product_id):
    values = Products.query.filter_by(product_id=product_id).first()
    values_all = Products.query.all()

    if "user" in session:
        if request.method == "POST":
            found_product = Products.query.filter_by(product_id=product_id).first()
            found_cart = cart.query.filter_by(email=session["email"])
            if found_product:
                data = cart(
                    name = found_product.name,
                    picture = found_product.picture,
                    product_id = product_id,
                    email = session["email"],
                    price = found_product.price
                )
                found_user = Users.query.filter_by(email=session["email"]).first()
                found_user.cart = int(found_user.cart) + 1
                db.session.add(data)
                db.session.commit()
                flash("Your product has been added to cart")
        return render_template("sign_product_show.html", cart=Users.query.filter_by(email=session["email"]).first(), values=values, user=session["user"], products=values_all)
    else:
        if request.method == "POST":
            return redirect(url_for("signin"))
        return render_template("nonsign_product_show.html", values=values, products=values_all)


@app.route("/cart", methods=["POST", "GET"])
def Cart_show():
    found_cart = cart.query.filter_by(email=session["email"]).all()
    cart_cart = Users.query.filter_by(email=session["email"]).first()
    total = 0

    for items in found_cart:
        total += items.price
    
    if request.method == "POST":
        name = request.form["name"]
        found_name = cart.query.filter_by(name=name).first()
        if found_name:
            db.session.delete(found_name)
            cart_cart.cart -= 1
            db.session.commit()

        return redirect(url_for("Cart_show"))

    return render_template("cart.html", values=found_cart, cart=cart_cart, total=total, user=session["user"])


@app.route("/proceedtoorder", methods=["POST", "GET"])
def proceed_to_order():
    if "user" in session:
        values = cart.query.filter_by(email=session["email"]).all()
        found_user = Users.query.filter_by(email=session["email"]).first()
        total = 0

        print(values)

        if values == []:
            flash("pls add products to cart to proceed to order")
            return redirect(url_for("Cart_show"))
        
        for items in values:
            total += items.price

        if request.method == "POST":
            for items in values:
                data = Purchased(
                    name = items.name,
                    picture = items.picture,
                    product_id = items.product_id,
                    price = items.price,
                    email = items.email
                )

                db.session.add(data)
                db.session.commit()

                found_item = cart.query.filter_by(name=items.name).first()

                db.session.delete(found_item)
                db.session.commit()

            found_user.cart = 0
            db.session.commit()

            flash("Thanks for shopping with E-Cart")
            return redirect(url_for("index"))

        return render_template("proceed.html", values=values, total=total)
    else:
        return redirect(url_for("index"))


@app.route("/ordersandplacements")
def orders_placements():
    if "user" in session:
        values = Purchased.query.filter_by(email=session["email"]).all()
        cart = Users.query.filter_by(email=session["email"]).first()
        return render_template("orders_placements.html", values=values, cart=cart, user=session["user"]) 
    else:
        return redirect(url_for("index"))

@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user")
        session.pop("email")
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
