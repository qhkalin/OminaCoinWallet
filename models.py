import uuid
import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)

# Global dictionaries for storing data
users = {}
wallets = {}
user_referrals = {}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    wallet_address = db.Column(db.String(32), unique=True, nullable=False)
    balance_coins = db.Column(db.Float, default=12.0)
    balance_usd = db.Column(db.Float, default=12.0)
    referral_code = db.Column(db.String(8), unique=True)
    is_withdrawal_unlocked = db.Column(db.Boolean, default=False)
    kyc_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.Float, default=time.time)
    last_login = db.Column(db.Float)
    deposit_confirmed = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.wallet_address = str(uuid.uuid4().hex)
        self.referral_code = str(uuid.uuid4())[:8]
        self.balance_coins = 12.0
        self.balance_usd = 12.0

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "wallet_address": self.wallet_address,
            "balance_coins": self.balance_coins,
            "balance_usd": self.balance_usd,
            "referral_code": self.referral_code,
            "is_withdrawal_unlocked": self.is_withdrawal_unlocked,
            "kyc_verified": self.kyc_verified,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "deposit_confirmed": self.deposit_confirmed,
            "is_admin": self.is_admin
        }

class Transaction:
    def __init__(self, sender_email, receiver_email, amount_coins, transaction_type="transfer"):
        self.transaction_id = str(uuid.uuid4())
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.amount_coins = amount_coins
        self.amount_usd = amount_coins  # 1:1 conversion
        self.timestamp = time.time()
        self.type = transaction_type  # "transfer", "purchase", "withdrawal", "bonus"

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "sender_email": self.sender_email,
            "receiver_email": self.receiver_email,
            "amount_coins": self.amount_coins,
            "amount_usd": self.amount_usd,
            "timestamp": self.timestamp,
            "type": self.type
        }

def get_user_referrals_count(email):
    """Get the number of users referred by the given email"""
    if email in user_referrals:
        return len(user_referrals[email])
    return 0

def apply_market_change(email, change_type):
    """Apply market price adjustments to a user's balance"""
    if email in users:
        user = users[email]
        if change_type == "drop":
            # Deduct 10% from balance
            user.balance_usd *= 0.9
            user.balance_coins *= 0.9
        elif change_type == "rise":
            # Multiply balance by 5x
            user.balance_usd *= 5
            user.balance_coins *= 5
        return True
    return False

def initialize_admin():
    """Initialize the admin account if it doesn't exist"""
    admin_email = "admin@ominacoin.com"
    if admin_email not in users:
        admin_user = User("197200", admin_email, "197200")
        admin_user.is_admin = True
        admin_user.balance_coins = 200000000000.0
        admin_user.balance_usd = 200000000000.0
        admin_user.is_withdrawal_unlocked = True
        admin_user.kyc_verified = True
        admin_user.deposit_confirmed = True

        users[admin_email] = admin_user
        wallets[admin_user.wallet_address] = admin_email

# Initialize the database
db.create_all()

# Initialize admin account
initialize_admin()