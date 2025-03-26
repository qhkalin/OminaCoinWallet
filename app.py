import os
import logging
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-for-omina-coin-wallet")

# Initialize JWT for authentication
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-for-omina-coin-wallet")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  # 24 hours

# Enable CORS
CORS(app)

# Import routes after app is created to avoid circular imports
from routes import *
