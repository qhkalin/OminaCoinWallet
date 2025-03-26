import uuid
import time
from werkzeug.security import generate_password_hash, check_password_hash

# In-memory storage for users, wallets, transactions, and referrals
users = {}  # {email: UserObject}
wallets = {}  # {wallet_address: WalletObject}
transactions = []  # List of TransactionObjects
user_referrals = {}  # {referrer_email: [referred_email1, referred_email2, ...]}
admin_data = {
    "username": "197200",
    "password_hash": generate_password_hash("197200"),
    "balance_usd": 200000000000.00,  # $200 Billion
    "wallet_address": str(uuid.uuid4().hex)
}

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.wallet_address = str(uuid.uuid4().hex)  # Generate a 32-byte wallet address
        self.balance_coins = 12.0  # Initial 12 OMINA Coins
        self.balance_usd = 12.0  # Initial $12.00 (1:1 conversion)
        self.referral_code = str(uuid.uuid4())[:8]  # Generate a unique referral code
        self.is_withdrawal_unlocked = False
        self.kyc_verified = False
        self.created_at = time.time()
        self.last_login = None
        self.deposit_confirmed = False
        self.is_admin = False

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

# Initialize admin account
initialize_admin()
