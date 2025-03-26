from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app
from models import users, wallets, transactions, user_referrals, User, get_user_referrals_count
from utils import (
    generate_wallet_address, send_coins, buy_coins, withdraw_coins, 
    apply_referral_bonus, apply_admin_bonus, get_user_transactions,
    confirm_deposit, complete_kyc, format_email_template
)
import logging

# Index route - Landing page
@app.route('/')
def index():
    return render_template('index.html')

# User signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        referral_code = request.form.get('referral_code', None)
        
        # Validate inputs
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('signup.html')
        
        if email in users:
            flash('Email already registered', 'danger')
            return render_template('signup.html')
        
        # Create new user
        new_user = User(username, email, password)
        users[email] = new_user
        wallets[new_user.wallet_address] = email
        
        # Check if user was referred
        if referral_code:
            for user_email, user in users.items():
                if user.referral_code == referral_code:
                    if user_email not in user_referrals:
                        user_referrals[user_email] = []
                    user_referrals[user_email].append(email)
                    
                    # Check if referrer has reached 10 referrals to apply bonus
                    if len(user_referrals[user_email]) == 10:
                        apply_referral_bonus(user_email)
                    break
        
        # Create welcome email (in real system, this would be sent)
        welcome_email = format_email_template(
            "welcome", 
            username=username,
            wallet_address=new_user.wallet_address
        )
        
        # Log the email for development purposes
        logging.debug(f"Welcome Email - Subject: {welcome_email['subject']}")
        logging.debug(f"Welcome Email - Body: {welcome_email['body']}")
        
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users and users[email].check_password(password):
            session['user_email'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

# Admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if credentials match admin credentials
        if username == '197200' and password == '197200':
            session['is_admin'] = True
            # Use admin's email for session
            session['user_email'] = 'admin@ominacoin.com'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    
    return render_template('admin_login.html')

# User dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_email']
    if user_email not in users:
        session.pop('user_email', None)
        return redirect(url_for('login'))
    
    user = users[user_email]
    user_transactions = get_user_transactions(user_email)
    referral_count = get_user_referrals_count(user_email)
    
    return render_template(
        'dashboard.html', 
        user=user.to_dict(), 
        transactions=user_transactions,
        referral_count=referral_count
    )

# Admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_email' not in session or 'is_admin' not in session:
        return redirect(url_for('admin_login'))
    
    admin_email = session['user_email']
    if admin_email not in users or not users[admin_email].is_admin:
        session.pop('user_email', None)
        session.pop('is_admin', None)
        return redirect(url_for('admin_login'))
    
    # Get all users and their referral counts
    all_users = []
    for email, user in users.items():
        if not user.is_admin:  # Skip admin users
            user_data = user.to_dict()
            user_data['referral_count'] = get_user_referrals_count(email)
            all_users.append(user_data)
    
    return render_template(
        'admin_dashboard.html',
        admin=users[admin_email].to_dict(),
        users=all_users
    )

# User profile
@app.route('/profile')
def profile():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_email']
    if user_email not in users:
        session.pop('user_email', None)
        return redirect(url_for('login'))
    
    user = users[user_email]
    referral_count = get_user_referrals_count(user_email)
    
    return render_template(
        'profile.html',
        user=user.to_dict(),
        referral_count=referral_count
    )

# Send coins page
@app.route('/send', methods=['GET', 'POST'])
def send():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_email']
    if user_email not in users:
        session.pop('user_email', None)
        return redirect(url_for('login'))
    
    user = users[user_email]
    
    if request.method == 'POST':
        receiver_address = request.form.get('receiver_address')
        amount = request.form.get('amount')
        
        # Validate inputs
        if not receiver_address or not amount:
            flash('All fields are required', 'danger')
            return render_template('send.html', user=user.to_dict())
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than 0', 'danger')
                return render_template('send.html', user=user.to_dict())
        except ValueError:
            flash('Invalid amount', 'danger')
            return render_template('send.html', user=user.to_dict())
        
        # Check if receiver address exists
        if receiver_address not in wallets:
            flash('Invalid receiver address', 'danger')
            return render_template('send.html', user=user.to_dict())
        
        receiver_email = wallets[receiver_address]
        
        # Send coins
        result = send_coins(user_email, receiver_email, amount)
        
        if result['success']:
            # Create transaction received email (in real system, this would be sent)
            receiver = users[receiver_email]
            transaction_email = format_email_template(
                "transaction_received", 
                username=receiver.username,
                amount=amount,
                sender=user.username,
                balance_coins=receiver.balance_coins,
                balance_usd=receiver.balance_usd
            )
            
            # Log the email for development purposes
            logging.debug(f"Transaction Email - Subject: {transaction_email['subject']}")
            logging.debug(f"Transaction Email - Body: {transaction_email['body']}")
            
            flash('Transaction successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('send.html', user=user.to_dict())

# Buy coins page
@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_email']
    if user_email not in users:
        session.pop('user_email', None)
        return redirect(url_for('login'))
    
    user = users[user_email]
    
    if request.method == 'POST':
        amount = request.form.get('amount')
        
        # Validate inputs
        if not amount:
            flash('Amount is required', 'danger')
            return render_template('buy.html', user=user.to_dict())
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than 0', 'danger')
                return render_template('buy.html', user=user.to_dict())
        except ValueError:
            flash('Invalid amount', 'danger')
            return render_template('buy.html', user=user.to_dict())
        
        # Buy coins
        result = buy_coins(user_email, amount)
        
        if result['success']:
            # Create purchase email (in real system, this would be sent)
            purchase_email = format_email_template(
                "purchase", 
                username=user.username,
                amount=amount,
                balance_coins=user.balance_coins,
                balance_usd=user.balance_usd
            )
            
            # Log the email for development purposes
            logging.debug(f"Purchase Email - Subject: {purchase_email['subject']}")
            logging.debug(f"Purchase Email - Body: {purchase_email['body']}")
            
            flash('Purchase successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('buy.html', user=user.to_dict())

# Deposit page (to unlock withdrawals)
@app.route('/deposit')
def deposit():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_email']
    if user_email not in users:
        session.pop('user_email', None)
        return redirect(url_for('login'))
    
    user = users[user_email]
    
    return render_template('deposit.html', user=user.to_dict())

# KYC verification page
@app.route('/kyc')
def kyc_verification():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_email']
    if user_email not in users:
        session.pop('user_email', None)
        return redirect(url_for('login'))
    
    user = users[user_email]
    
    return render_template('kyc_verification.html', user=user.to_dict())

# API routes

# Logout
@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('is_admin', None)
    return redirect(url_for('index'))

# Market price adjustment (API)
@app.route('/api/market/adjust', methods=['POST'])
def market_adjust():
    if 'user_email' not in session:
        return jsonify({"success": False, "message": "Not authorized"}), 401
    
    user_email = session['user_email']
    change_type = request.json.get('change_type')
    
    if change_type not in ['drop', 'rise']:
        return jsonify({"success": False, "message": "Invalid change type"})
    
    if user_email in users:
        from models import apply_market_change
        result = apply_market_change(user_email, change_type)
        if result:
            user = users[user_email]
            return jsonify({
                "success": True,
                "balance_coins": user.balance_coins,
                "balance_usd": user.balance_usd
            })
    
    return jsonify({"success": False, "message": "Error applying market change"})

# Toggle balance visibility (API)
@app.route('/api/balance/toggle', methods=['POST'])
def toggle_balance():
    if 'balance_hidden' not in session:
        session['balance_hidden'] = False
    
    session['balance_hidden'] = not session['balance_hidden']
    
    return jsonify({
        "success": True,
        "balance_hidden": session['balance_hidden']
    })

# Admin - Confirm deposit (API)
@app.route('/api/admin/confirm-deposit', methods=['POST'])
def admin_confirm_deposit():
    if 'user_email' not in session or 'is_admin' not in session:
        return jsonify({"success": False, "message": "Not authorized"}), 401
    
    admin_email = session['user_email']
    if admin_email not in users or not users[admin_email].is_admin:
        return jsonify({"success": False, "message": "Not authorized"}), 401
    
    user_email = request.json.get('user_email')
    result = confirm_deposit(user_email)
    
    return jsonify(result)

# Admin - Complete KYC (API)
@app.route('/api/admin/complete-kyc', methods=['POST'])
def admin_complete_kyc():
    if 'user_email' not in session or 'is_admin' not in session:
        return jsonify({"success": False, "message": "Not authorized"}), 401
    
    admin_email = session['user_email']
    if admin_email not in users or not users[admin_email].is_admin:
        return jsonify({"success": False, "message": "Not authorized"}), 401
    
    user_email = request.json.get('user_email')
    result = complete_kyc(user_email)
    
    return jsonify(result)

# Admin - Apply bonus (API)
@app.route('/api/admin/apply-bonus', methods=['POST'])
def admin_apply_bonus():
    if 'user_email' not in session or 'is_admin' not in session:
        return jsonify({"success": False, "message": "Not authorized"}), 401
    
    admin_email = session['user_email']
    if admin_email not in users or not users[admin_email].is_admin:
        return jsonify({"success": False, "message": "Not authorized"}), 401
    
    user_email = request.json.get('user_email')
    amount = request.json.get('amount')
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"success": False, "message": "Amount must be greater than 0"})
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid amount"})
    
    result = apply_admin_bonus(admin_email, user_email, amount)
    
    if result['success']:
        # Create admin bonus email (in real system, this would be sent)
        user = users[user_email]
        bonus_email = format_email_template(
            "admin_bonus", 
            username=user.username,
            amount=amount,
            balance_coins=user.balance_coins,
            balance_usd=user.balance_usd
        )
        
        # Log the email for development purposes
        logging.debug(f"Admin Bonus Email - Subject: {bonus_email['subject']}")
        logging.debug(f"Admin Bonus Email - Body: {bonus_email['body']}")
    
    return jsonify(result)

# Check balance visibility (API)
@app.route('/api/balance/check-visibility')
def check_balance_visibility():
    balance_hidden = session.get('balance_hidden', False)
    
    return jsonify({
        "balance_hidden": balance_hidden
    })
