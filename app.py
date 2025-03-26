import os
import logging
import datetime
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-for-omina-coin-wallet")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///omina.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize JWT for authentication
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-for-omina-coin-wallet")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  # 24 hours

# Enable CORS
CORS(app)

# Custom Jinja2 filters
@app.template_filter('strftime')
def _jinja2_filter_datetime(timestamp, fmt=None):
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M:%S'
    if isinstance(timestamp, (int, float)):
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime(fmt)
    return timestamp

@app.template_filter('format_currency')
def _jinja2_filter_currency(value):
    """Format a value as USD currency."""
    if value is None:
        return "$0.00"
    return "${:,.2f}".format(float(value))

# Import routes after app is created to avoid circular imports
from routes import *
