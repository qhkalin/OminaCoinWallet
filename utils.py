import uuid
from models import users, wallets, transactions, user_referrals, Transaction

def generate_wallet_address():
    """Generate a unique 32-byte wallet address"""
    return str(uuid.uuid4().hex)

def send_coins(sender_email, receiver_email, amount):
    """Send coins from one user to another"""
    if sender_email not in users or receiver_email not in users:
        return {"success": False, "message": "Invalid sender or receiver"}
    
    sender = users[sender_email]
    receiver = users[receiver_email]
    
    if sender.balance_coins < float(amount):
        return {"success": False, "message": "Insufficient balance"}
    
    # Update balances
    sender.balance_coins -= float(amount)
    sender.balance_usd -= float(amount)  # 1:1 conversion
    
    receiver.balance_coins += float(amount)
    receiver.balance_usd += float(amount)  # 1:1 conversion
    
    # Record transaction
    transaction = Transaction(sender_email, receiver_email, float(amount))
    transactions.append(transaction)
    
    return {
        "success": True, 
        "message": "Transaction successful",
        "transaction_id": transaction.transaction_id
    }

def buy_coins(user_email, amount):
    """Buy coins using USD balance"""
    if user_email not in users:
        return {"success": False, "message": "User not found"}
    
    user = users[user_email]
    amount = float(amount)
    
    if user.balance_usd < amount:
        return {"success": False, "message": "Insufficient USD balance"}
    
    # Update balances
    user.balance_usd -= amount
    user.balance_coins += amount  # 1:1 conversion
    
    # Record transaction
    transaction = Transaction("system", user_email, amount, "purchase")
    transactions.append(transaction)
    
    return {
        "success": True, 
        "message": "Purchase successful",
        "transaction_id": transaction.transaction_id
    }

def withdraw_coins(user_email, amount):
    """Withdraw coins (simulate)"""
    if user_email not in users:
        return {"success": False, "message": "User not found"}
    
    user = users[user_email]
    amount = float(amount)
    
    if not user.is_withdrawal_unlocked:
        return {"success": False, "message": "Withdrawal not unlocked. Please make a deposit first."}
    
    if not user.kyc_verified:
        return {"success": False, "message": "KYC verification required for withdrawal"}
    
    if user.balance_coins < amount:
        return {"success": False, "message": "Insufficient coin balance"}
    
    # Update balances
    user.balance_coins -= amount
    user.balance_usd -= amount  # 1:1 conversion
    
    # Record transaction
    transaction = Transaction(user_email, "withdrawal", amount, "withdrawal")
    transactions.append(transaction)
    
    return {
        "success": True, 
        "message": "Withdrawal processing",
        "transaction_id": transaction.transaction_id
    }

def apply_referral_bonus(user_email):
    """Apply bonus for users with 10+ referrals"""
    if user_email not in users:
        return {"success": False, "message": "User not found"}
    
    if user_email not in user_referrals or len(user_referrals[user_email]) < 10:
        return {"success": False, "message": "Not enough referrals"}
    
    # User has 10+ referrals, apply bonus
    bonus_amount = 20.0  # $20 bonus
    user = users[user_email]
    
    user.balance_coins += bonus_amount
    user.balance_usd += bonus_amount
    
    # Record transaction
    transaction = Transaction("system", user_email, bonus_amount, "bonus")
    transactions.append(transaction)
    
    return {
        "success": True, 
        "message": "Referral bonus applied",
        "bonus_amount": bonus_amount,
        "transaction_id": transaction.transaction_id
    }

def apply_admin_bonus(admin_email, user_email, amount):
    """Admin sends bonus to a user"""
    if admin_email not in users or not users[admin_email].is_admin:
        return {"success": False, "message": "Not authorized"}
    
    if user_email not in users:
        return {"success": False, "message": "User not found"}
    
    user = users[user_email]
    admin = users[admin_email]
    amount = float(amount)
    
    user.balance_coins += amount
    user.balance_usd += amount
    
    # Record transaction
    transaction = Transaction(admin_email, user_email, amount, "bonus")
    transactions.append(transaction)
    
    return {
        "success": True, 
        "message": "Admin bonus sent",
        "transaction_id": transaction.transaction_id
    }

def get_user_transactions(user_email):
    """Get all transactions for a specific user"""
    user_transactions = []
    
    for transaction in transactions:
        if transaction.sender_email == user_email or transaction.receiver_email == user_email:
            user_transactions.append(transaction.to_dict())
    
    return sorted(user_transactions, key=lambda x: x["timestamp"], reverse=True)

def confirm_deposit(user_email):
    """Confirm a user's deposit and unlock withdrawals"""
    if user_email not in users:
        return {"success": False, "message": "User not found"}
    
    user = users[user_email]
    user.deposit_confirmed = True
    user.is_withdrawal_unlocked = True
    
    return {"success": True, "message": "Deposit confirmed and withdrawals unlocked"}

def complete_kyc(user_email):
    """Complete KYC verification for a user"""
    if user_email not in users:
        return {"success": False, "message": "User not found"}
    
    user = users[user_email]
    user.kyc_verified = True
    
    return {"success": True, "message": "KYC verification completed"}

def format_email_template(template_type, **kwargs):
    """Format email templates for different actions"""
    templates = {
        "welcome": {
            "subject": "Welcome to OMINA Wallet – Your Crypto Journey Begins!",
            "body": f"""
            Dear {kwargs.get('username', '')}, your OMINA Wallet has been created successfully! 🎉
            Your Wallet Address: {kwargs.get('wallet_address', '')}
            Your starting balance: 12 XXXXXXXX012 ($12.00)
            Start referring users & earning rewards now!
            """
        },
        "transaction_received": {
            "subject": "You've received OMINA Coins!",
            "body": f"""
            Dear {kwargs.get('username', '')}, you have received {kwargs.get('amount', '')} OMINA Coins from {kwargs.get('sender', '')}.
            New Balance: {kwargs.get('balance_coins', '')} XXXXXXXX012 (${kwargs.get('balance_usd', '')})
            """
        },
        "purchase": {
            "subject": "You've Purchased OMINA Coins!",
            "body": f"""
            Dear {kwargs.get('username', '')}, you have successfully purchased {kwargs.get('amount', '')} XXXXXXXX012 Coins.
            New Coin Balance: {kwargs.get('balance_coins', '')}
            New USD Balance: ${kwargs.get('balance_usd', '')}
            """
        },
        "referral_bonus": {
            "subject": "Congratulations! You've Earned a Referral Bonus!",
            "body": f"""
            Dear {kwargs.get('username', '')}, you have successfully referred 10 users!
            You've earned {kwargs.get('bonus_amount', '')} XXXXXXXX012 (${kwargs.get('bonus_usd', '')})
            New Balance: {kwargs.get('balance_coins', '')} XXXXXXXX012 (${kwargs.get('balance_usd', '')})
            """
        },
        "kyc_verification": {
            "subject": "KYC Verification Required for Withdrawal",
            "body": f"""
            Dear {kwargs.get('username', '')}, we noticed unusual activity on your account.
            Please contact customer support for verification.
            """
        },
        "withdrawal": {
            "subject": "Your Withdrawal is Processing!",
            "body": f"""
            Dear {kwargs.get('username', '')}, you have successfully withdrawn {kwargs.get('amount', '')} XXXXXXXX012 Coins.
            New USD Balance: ${kwargs.get('balance_usd', '')}
            """
        },
        "admin_bonus": {
            "subject": "Admin Reward: Referral Bonus Credited!",
            "body": f"""
            Dear {kwargs.get('username', '')}, the admin has sent you a referral bonus of {kwargs.get('amount', '')} XXXXXXXX012 Coins.
            New Balance: {kwargs.get('balance_coins', '')} XXXXXXXX012 (${kwargs.get('balance_usd', '')})
            """
        },
    }
    
    return templates.get(template_type, {"subject": "OMINA Wallet Notification", "body": "No content"})
