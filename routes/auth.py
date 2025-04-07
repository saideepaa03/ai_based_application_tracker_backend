from flask import request, jsonify
from db import db
from models import User
from routes import auth_bp  # Import the Blueprint
from werkzeug.security import generate_password_hash, check_password_hash

# User Signup
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name, email, password, role = data["name"], data["email"], data["password"], data["role"]

    if role not in ["candidate", "recruiter"]:
        return jsonify({"error": "Invalid role"}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 409  # HTTP 409 Conflict

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password_hash=hashed_password, role=role)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User created successfully"}), 201

# User Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email, password = data["email"], data["password"]

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return jsonify({"message": "Login successful", "user": user.to_json()}), 200
    return jsonify({"error": "Invalid credentials"}), 401
