from flask import Flask, render_template, request, session, redirect, url_for
from elasticsearch import Elasticsearch
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required to use session for storing cart data

# Connect to Elasticsearch
es = Elasticsearch(
    ["host:port"],
    basic_auth=("username", "password")
)

# Home route to show categories
@app.route("/")
def home():
    categories = ['Apparel', 'Footwear', 'Accessories', 'Beauty', 'Sportswear']
    return render_template("index.html", categories=categories)

# Category search route
@app.route("/category/<category_name>", methods=["GET"])
def category_search(category_name):
    page = int(request.args.get("page", 1))  # Get page number from query parameter, default to 1
    per_page = 50
    start = (page - 1) * per_page

    # Query to search products by category using "match" for flexible search
    search_body = {
        "query": {
            "match": {
                "Category": category_name
            }
        },
        "from": start,
        "size": per_page
    }

    results = es.search(index="products", body=search_body)
    products = [hit["_source"] for hit in results["hits"]["hits"]]
    total_hits = results["hits"]["total"]["value"]

    return render_template(
        "results.html",
        products=products,
        query=category_name,
        category_filter=category_name,
        total_hits=total_hits,
        page=page,
        per_page=per_page
    )

# Search route for handling user input from the search box
@app.route("/search", methods=["POST", "GET"])
def search():
    query = request.form.get('query', request.args.get('query', ''))
    page = int(request.args.get("page", 1))  # Get page number from query parameter, default to 1
    per_page = 50
    start = (page - 1) * per_page

    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["ProductTitle", "Category", "ProductType", "SubCategory", "Colour"]
            }
        },
        "from": start,
        "size": per_page
    }

    results = es.search(index="products", body=search_body)
    products = [hit["_source"] for hit in results["hits"]["hits"]]
    total_hits = results["hits"]["total"]["value"]

    return render_template(
        "results.html",
        products=products,
        query=query,
        category_filter=None,
        total_hits=total_hits,
        page=page,
        per_page=per_page
    )

# Route to add item to cart
@app.route("/add_to_cart/<product_id>")
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(product_id)
    session.modified = True
    return redirect(url_for("view_cart"))

# Route to view cart items
@app.route("/cart")
def view_cart():
    cart = session.get("cart", [])
    cart_items = []

    for product_id in cart:
        search_body = {
            "query": {
                "term": {
                    "ProductId": product_id
                }
            }
        }
        result = es.search(index="products", body=search_body)
        if result["hits"]["hits"]:
            cart_items.append(result["hits"]["hits"][0]["_source"])

    return render_template("cart.html", cart_items=cart_items)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5030, debug=True)
