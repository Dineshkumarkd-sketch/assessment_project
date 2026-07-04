from flask import Blueprint, request, jsonify
from database import mongo
from auth import hash_password, check_password, generate_token, decode_token
from bson.objectid import ObjectId
from functools import wraps

api = Blueprint('api', __name__)

# =========================
# SAFE DB CHECK
# =========================
def check_db():
    if mongo.db is None:
        raise Exception("Database not connected")

# =========================
# TOKEN MIDDLEWARE
# =========================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            check_db()

            token = None

            if 'Authorization' in request.headers:
                parts = request.headers['Authorization'].split()
                if len(parts) == 2 and parts[0] == 'Bearer':
                    token = parts[1]

            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            user_id = decode_token(token)

            if isinstance(user_id, str):
                return jsonify({'message': user_id}), 401

            current_user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

            if not current_user:
                return jsonify({'message': 'User not found!'}), 401

            return f(current_user, *args, **kwargs)

        except Exception as e:
            print("TOKEN ERROR:", str(e))
            return jsonify({'message': 'Server error'}), 500

    return decorated


# =========================
# REGISTER
# =========================
@api.route('/auth/register', methods=['POST'])
def register():
    try:
        check_db()

        data = request.get_json()

        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Missing email or password'}), 400

        email = data['email']

        if mongo.db.users.find_one({"email": email}):
            return jsonify({'message': 'User already exists'}), 400

        hashed_password = hash_password(data['password'])

        user_id = mongo.db.users.insert_one({
            "email": email,
            "password": hashed_password,
            "name": data.get('name', '')
        }).inserted_id

        token = generate_token(str(user_id))

        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': str(user_id),
                'email': email,
                'name': data.get('name', '')
            }
        }), 201

    except Exception as e:
        print("REGISTER ERROR:", str(e))
        return jsonify({'message': str(e)}), 500


# =========================
# LOGIN
# =========================
@api.route('/auth/login', methods=['POST'])
def login():
    try:
        check_db()

        data = request.get_json()

        if not data:
            return jsonify({'message': 'Missing data'}), 400

        user = mongo.db.users.find_one({"email": data.get('email')})

        if not user or not check_password(data.get('password'), user['password']):
            return jsonify({'message': 'Invalid credentials'}), 401

        token = generate_token(str(user['_id']))

        return jsonify({
            'token': token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user.get('name', '')
            }
        }), 200

    except Exception as e:
        print("LOGIN ERROR:", str(e))
        return jsonify({'message': 'Server error'}), 500


# =========================
# GET PRODUCTS
# =========================
@api.route('/products', methods=['GET'])
@token_required
def get_products(current_user):
    try:
        products = []

        for p in mongo.db.products.find({"user_id": str(current_user['_id'])}):
            p['_id'] = str(p['_id'])
            products.append(p)

        return jsonify(products), 200

    except Exception as e:
        print("GET PRODUCTS ERROR:", str(e))
        return jsonify({'message': 'Server error'}), 500


# =========================
# CREATE PRODUCT
# =========================
@api.route('/products', methods=['POST'])
@token_required
def create_product(current_user):
    try:
        data = request.get_json()

        product_id = mongo.db.products.insert_one({
            "name": data.get('name'),
            "description": data.get('description', ''),
            "price": float(data.get('price', 0)),
            "category": data.get('category', ''),
            "user_id": str(current_user['_id'])
        }).inserted_id

        product = mongo.db.products.find_one({"_id": product_id})
        product['_id'] = str(product['_id'])

        return jsonify(product), 201

    except Exception as e:
        print("CREATE PRODUCT ERROR:", str(e))
        return jsonify({'message': 'Server error'}), 500


# =========================
# UPDATE PRODUCT
# =========================
@api.route('/products/<product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    try:
        data = request.get_json()

        product = mongo.db.products.find_one({
            "_id": ObjectId(product_id),
            "user_id": str(current_user['_id'])
        })

        if not product:
            return jsonify({'message': 'Not found'}), 404

        update_data = {}

        if 'name' in data:
            update_data['name'] = data['name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'price' in data:
            update_data['price'] = float(data['price'])
        if 'category' in data:
            update_data['category'] = data['category']

        mongo.db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )

        updated = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        updated['_id'] = str(updated['_id'])

        return jsonify(updated), 200

    except Exception as e:
        print("UPDATE ERROR:", str(e))
        return jsonify({'message': 'Server error'}), 500


# =========================
# DELETE PRODUCT
# =========================
@api.route('/products/<product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    try:
        result = mongo.db.products.delete_one({
            "_id": ObjectId(product_id),
            "user_id": str(current_user['_id'])
        })

        if result.deleted_count == 0:
            return jsonify({'message': 'Not found'}), 404

        return jsonify({'message': 'Deleted successfully'}), 200

    except Exception as e:
        print("DELETE ERROR:", str(e))
        return jsonify({'message': 'Server error'}), 500