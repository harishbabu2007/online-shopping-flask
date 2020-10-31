from flask import Flask, render_template, flash, request, redirect, url_for, session
from datetime import timedelta
import requests
from flask_sqlalchemy import SQLAlchemy
import flask_whooshalchemy as wa

app = Flask(__name__)
app.secret_key = "@$#^$%^$%*&DBG%^^$$%^$%^$%^$%$GFGJHJTYJTYHNT"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///db.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["WHOOSH_BASE"] = "whoosh"
app.permanent_session_lifetime = timedelta(days=365)

db = SQLAlchemy(app)

class Admin(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    password = db.Column("password", db.String(100), nullable=False)

    def __init__(self, name, password):
        self.name = name
        self.password = password

class YourProducts(db.Model):
    __searchable__ = ["name", "company", "search_terms"]

    name = db.Column("name", db.String(100), nullable=False)
    picture = db.Column("picture", db.String(1000), nullable=False)
    product_id = db.Column("product_id", db.Integer, primary_key=True)
    price = db.Column("price", db.Integer, nullable=False)
    stock = db.Column("stock", db.Integer, nullable=False)
    company = db.Column("company", db.String(100), nullable=False)
    search_terms = db.Column("search_terms", db.String(1000), nullable=True)
    description = db.Column("description", db.String(1000), nullable=False)
    category = db.Column("category", db.String(100), nullable=False)
    pucrhases = db.Column("purchases", db.Integer)

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

wa.whoosh_index(app, YourProducts)

@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        username = request.form["username"]
        password = request.form["password"]
        found_user = Admin.query.filter_by(name=username).first()

        if found_user:
            if found_user.password == password:
                session["user"] = username
                return redirect(url_for("admin_panel"))
            else:
                flash("invalid password")
                return redirect(url_for("login"))
        else:
            flash("invalid username")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/admin")
def admin_panel():
    if "user" in session:
        return render_template("admin.html", values=YourProducts.query.all())
    else:
        return redirect(url_for("login"))


@app.route("/search", methods=["POST", "GET"])
def search():
    product = YourProducts.query.whoosh_search(request.args.get("query")).all()
    return render_template("admin.html", values=product)


@app.route("/addproduct", methods=["POST", "GET"])
def add_product():
    if request.method == "POST":
        product_id = request.form["product_id"]
        found_product_id = YourProducts.query.filter_by(product_id=product_id).first()
        if not found_product_id:
            data = {
                "name": request.form["name"],
                "product_id": product_id,
                "picture": request.form["picture"],
                "price": request.form["price"],
                "stock": request.form["stock"],
                "company": request.form["company"],
                "search_terms": request.form["search_terms"],
                "description": request.form["description"],
                "category": request.form["category"]
            }

            product_add = YourProducts(
                name = request.form["name"],
                product_id = product_id,
                price = request.form["price"],
                stock = request.form["stock"],
                picture = request.form["picture"],
                company = request.form["company"],
                search_terms = request.form["search_terms"],
                description = request.form["description"],
                category = request.form["category"]
            )

            req = requests.put(f"http://127.0.0.1:5000/apifororders/getorders/{product_id}", data)

            if req.status_code == 409:
                flash("Product was not added succesfully. Please fill in the product detalis properly or try giving another product ID")
                return redirect(url_for("add_product"))
            else:
                flash("Product added to E-Cart succesfully")
                db.session.add(product_add)
                db.session.commit()
                return redirect(url_for("add_product"))
        else:
            flash("Product was not added succesfully. Please fill in the product detalis properly or try giving another product ID")
            return redirect(url_for("add_product"))

        return redirect(url_for("add_product"))

    return render_template("add_product.html")

@app.route("/updatestock", methods=["POST", "GET"])
def update_stock():
    if request.method == "POST":
        product_id = request.form["product_id"]
        data = {
            "stock": request.form["stock"],
        }

        req = requests.patch("http://127.0.0.1:5000/apifororders/updatestock/" + request.form["product_id"], data)

        if req.status_code == 409:
            flash("Product was not updated succesfully. Please try giving a valid product id")
            return redirect(url_for("update_stock"))
        else:
            flash("Product was updated succesfully")
            return redirect(url_for("update_stock"))
        
    return render_template("update_stock.html")


@app.route("/deleteproduct", methods=["POST", "GET"])
def delete_product():
    if request.method == "POST":
        product_id = request.form["product_id"]
        found_product_id = YourProducts.query.filter_by(product_id=product_id).delete()

        if found_product_id:

            db.delete(table=YourProducts)
            db.session.commit()

            req = requests.delete(f"http://127.0.0.1:5000/apifororders/deleteproduct/{product_id}")

            if req.status_code == 409:
                flash("Product was not deleted succesfully. Please try giving a valid product id")
                return redirect(url_for("delete_product"))
            else:
                flash("Product was deleted succesfully")
                return redirect(url_for("delete_product"))
        else:
            flash("Product was not deleted succesfully. Please try giving a valid product id")
            return redirect(url_for("delete_product"))

    return render_template("delete_product.html")


if __name__ == "__main__":
    db.create_all()
    app.run(port='5080', debug=True)