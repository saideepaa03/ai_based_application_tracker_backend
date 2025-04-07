from flask import Blueprint

# Initialize Blueprints
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
user_bp = Blueprint("user", __name__, url_prefix="/user")

# Import routes to register them
from routes import auth, user
