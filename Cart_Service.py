import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Sample data
carts = [
    # {"cart id": 1, "products": [{"name": "onions", "quantity": 2, "total price": 1.98},
    #                             {"name": "beef", "quantity": 1, "total price": 12.99}], "purchase total": 14.97},
    # {"cart id": 2, "products": [{"name": "beef", "quantity": 1, "total price": 12.99},
    #                             {"name": "shampoo", "quantity": 1, "total price": 7.99}], "purchase total": 20.98},
    # {"cart id": 3, "products": [{"name": "shampoo", "quantity": 1, "total price": 7.99}], "purchase total": 7.99},
    # {"cart id": 4, "products": [{"name": "shampoo", "quantity": 1, "total price": 7.99}], "purchase total": 7.99}
    {"cart id": 1, "products": [], "purchase total": 0.00},
    {"cart id": 2, "products": [], "purchase total": 0.00},
    {"cart id": 3, "products": [], "purchase total": 0.00},
    {"cart id": 4, "products": [], "purchase total": 0.00},
    {"cart id": 5, "products": [], "purchase total": 0.00}
]


# Endpoint 1: Get content of specified cart
@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    cart = next((cart for cart in carts if cart["cart id"] == user_id), None)
    if cart:
        return jsonify(cart), 201
    else:
        return jsonify({"Error": "Cart not found"}), 404


# Endpoint 2: Remove one unit of a product from the cart
@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_product(user_id, product_id):
    cart = next((cart for cart in carts if cart["cart id"] == user_id), None)
    total = cart["purchase total"]
    product = requests.get(f'https://product-service-7squ.onrender.com/products/{product_id}')
    prod = product.json()
    p_id = prod["Product"]["id"]
    price = prod["Product"]["price"]
    name = prod["Product"]["name"]
    item = next((item for item in cart["products"] if item["name"] == name), None)
    if item ==  None:
        return jsonify({"Error": "Product is not in cart"})
    item["quantity"] -= 1
    # If a product has a new quantity of 0 in the cart, then remove it entirely from the cart
    if item["quantity"] == 0:
        for i, dic in enumerate(cart["products"]):
            if dic["name"] == name:
                index = i
        cart["products"].remove(cart["products"][index])
    item["total price"] = round((item["total price"] - price), 2)
    cart["purchase total"] = round((total - price), 2)
    # Add one unit of product in product service
    new_json = {
        "id": p_id,
        "name": name,
        "units_in_stock": 1
    }
    response = requests.post(f'https://product-service-7squ.onrender.com/products/{product_id}', json=new_json)
    return jsonify({"Cart": cart}), 201


# Endpoint 3: Add one unit of a product to the cart
@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_product(user_id, product_id):
    cart = next((cart for cart in carts if cart["cart id"] == user_id), None)
    total = cart["purchase total"]
    product = requests.get(f'https://product-service-7squ.onrender.com/products/{product_id}')
    prod = product.json()
    quantity = prod["Product"]["units_in_stock"]
    p_id = prod["Product"]["id"]
    price = prod["Product"]["price"]
    name = prod["Product"]["name"]
    # Add one unit of product to cart only if it is in stock
    if quantity > 0:
        item = next((item for item in cart["products"] if item["name"] == name), None)
        if item == None:
            cart["products"].append({"name": name, "quantity": 1, "total price": price})
        else:
            item["quantity"] += 1
            item["total price"] = round((item["total price"] + price), 2)
        cart["purchase total"] = round((total + price), 2)
        # Subtract one unit of product from product service
        new_json = {
            "id": p_id,
            "name": name,
            "units_in_stock": -1
        }
        response = requests.post(f'https://product-service-7squ.onrender.com/products/{product_id}', json=new_json)
        return jsonify({"Cart": cart}), 201
    else:
        return jsonify({"Error": "Product is out of stock"}), 404

if __name__ == '__main__':
    app.run(debug=False)
