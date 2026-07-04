from flask import Blueprint, request, jsonify, current_app
from database import mongo
from auth import hash_password, check_password, generate_token, decode_token
from bson.objectid import ObjectId
from functools import wraps

api = Blueprint('api', __name__)

# Authentication middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # JWT is passed in the request header
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        user_id = decode_token(token)
        
        if isinstance(user_id, str) and (user_id.startswith('Signature expired') or user_id.startswith('Invalid token')):
            return jsonify({'message': user_id}), 401
            
        current_user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        
        if not current_user:
            return jsonify({'message': 'User not found!'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

@api.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
        
    email = data['email']
    password = data['password']
    
    # Check if user already exists
    if mongo.db.users.find_one({"email": email}):
        return jsonify({'message': 'User already exists'}), 400
        
    hashed_password = hash_password(password)
    
    user_id = mongo.db.users.insert_one({
        "email": email,
        "password": hashed_password,
        "name": data.get('name', '')
    }).inserted_id
    
    return jsonify({'message': 'User registered successfully', 'userId': str(user_id)}), 201

@api.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
        
    user = mongo.db.users.find_one({"email": data['email']})
    
    if not user or not check_password(data['password'], user['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
        
    token = generate_token(str(user['_id']))
    
    return jsonify({'token': token, 'user': {'email': user['email'], 'name': user.get('name', ''), 'id': str(user['_id'])} }), 200

# Product CRUD operations
@api.route('/products', methods=['GET'])
@token_required
def get_products(current_user):
    products = []
    # Find products belonging to the current user
    for product in mongo.db.products.find({"user_id": str(current_user['_id'])}):
        product['_id'] = str(product['_id'])
        products.append(product)
    return jsonify(products), 200

@api.route('/products', methods=['POST'])
@token_required
def create_product(current_user):
    data = request.get_json()
    if not data or not data.get('name') or not data.get('price'):
        return jsonify({'message': 'Missing required fields (name, price)'}), 400
        
    product_id = mongo.db.products.insert_one({
        "name": data['name'],
        "description": data.get('description', ''),
        "price": float(data['price']),
        "category": data.get('category', ''),
        "user_id": str(current_user['_id'])
    }).inserted_id
    
    new_product = mongo.db.products.find_one({"_id": product_id})
    new_product['_id'] = str(new_product['_id'])
    
    return jsonify(new_product), 201

@api.route('/products/<product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    data = request.get_json()
    
    # Verify product belongs to user
    product = mongo.db.products.find_one({"_id": ObjectId(product_id), "user_id": str(current_user['_id'])})
    if not product:
        return jsonify({'message': 'Product not found or unauthorized'}), 404
        
    update_data = {}
    if 'name' in data: update_data['name'] = data['name']
    if 'description' in data: update_data['description'] = data['description']
    if 'price' in data: update_data['price'] = float(data['price'])
    if 'category' in data: update_data['category'] = data['category']
    
    if update_data:
        mongo.db.products.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})
        
    updated_product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    updated_product['_id'] = str(updated_product['_id'])
    
    return jsonify(updated_product), 200

@api.route('/products/<product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    result = mongo.db.products.delete_one({"_id": ObjectId(product_id), "user_id": str(current_user['_id'])})
    
    if result.deleted_count == 0:
        return jsonify({'message': 'Product not found or unauthorized'}), 404
        
    return jsonify({'message': 'Product deleted successfully'}), 200
