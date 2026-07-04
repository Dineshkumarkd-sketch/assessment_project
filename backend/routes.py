from flask import Blueprint, request, jsonify
from database import mongo
from auth import hash_password, check_password, generate_token, decode_token
from bson.objectid import ObjectId
from functools import wraps

api = Blueprint("api", __name__)


# ================= TOKEN MIDDLEWARE =================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        auth = request.headers.get("Authorization")

        if auth and auth.startswith("Bearer "):
            token = auth.split(" ")[1]

        if not token:
            return jsonify({"message": "Token missing"}), 401

        user_id = decode_token(token)

        # Invalid token check
        if user_id == "Invalid token. Please log in again." or \
           user_id == "Signature expired. Please log in again.":
            return jsonify({"message": user_id}), 401

        try:
            current_user = mongo.db.users.find_one({
                "_id": ObjectId(user_id)
            })
        except Exception:
            return jsonify({"message": "Invalid user id"}), 401

        if current_user is None:
            return jsonify({"message": "User not found"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# ================= REGISTER =================

@api.route("/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")
        name = data.get("name", "")

        if not email or not password:
            return jsonify({"message": "Missing fields"}), 400

        if mongo.db.users.find_one({"email": email}):
            return jsonify({"message": "User already exists"}), 400

        hashed = hash_password(password)

        result = mongo.db.users.insert_one({
            "email": email,
            "password": hashed,
            "name": name
        })

        token = generate_token(str(result.inserted_id))

        return jsonify({
            "message": "User registered successfully",
            "token": token,
            "user": {
                "id": str(result.inserted_id),
                "email": email,
                "name": name
            }
        }), 201

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"message": str(e)}), 500


# ================= LOGIN =================

@api.route("/auth/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = mongo.db.users.find_one({"email": email})

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    if not check_password(password, user["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    token = generate_token(str(user["_id"]))

    return jsonify({
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user.get("name", "")
        }
    })


# ================= GET PRODUCTS =================

@api.route("/products", methods=["GET"])
@token_required
def get_products(current_user):

    products = []

    for p in mongo.db.products.find({
        "user_id": str(current_user["_id"])
    }):
        p["_id"] = str(p["_id"])
        products.append(p)

    return jsonify(products), 200


# ================= ADD PRODUCT =================

@api.route("/products", methods=["POST"])
@token_required
def create_product(current_user):

    data = request.get_json()

    result = mongo.db.products.insert_one({
        "name": data.get("name"),
        "description": data.get("description"),
        "price": float(data.get("price", 0)),
        "category": data.get("category"),
        "user_id": str(current_user["_id"])
    })

    product = mongo.db.products.find_one({
        "_id": result.inserted_id
    })

    product["_id"] = str(product["_id"])

    return jsonify(product), 201


# ================= UPDATE PRODUCT =================

@api.route("/products/<product_id>", methods=["PUT"])
@token_required
def update_product(current_user, product_id):

    data = request.get_json()

    mongo.db.products.update_one(
        {
            "_id": ObjectId(product_id),
            "user_id": str(current_user["_id"])
        },
        {
            "$set": {
                "name": data.get("name"),
                "description": data.get("description"),
                "price": float(data.get("price")),
                "category": data.get("category")
            }
        }
    )

    product = mongo.db.products.find_one({
        "_id": ObjectId(product_id)
    })

    product["_id"] = str(product["_id"])

    return jsonify(product)


# ================= DELETE PRODUCT =================

@api.route("/products/<product_id>", methods=["DELETE"])
@token_required
def delete_product(current_user, product_id):

    mongo.db.products.delete_one({
        "_id": ObjectId(product_id),
        "user_id": str(current_user["_id"])
    })

    return jsonify({
        "message": "Deleted successfully"
    })