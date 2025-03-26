from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app
from models import db, User, get_user_referrals_count
from utils import (
    generate_wallet_address, send_coins, buy_coins, withdraw_coins, 
    apply_referral_bonus, apply_admin_bonus, get_user_transactions,
    confirm_deposit, complete_kyc, format_email_template
)
from email_utils import (
    send_welcome_email, send_transaction_email, send_purchase_email,
    send_referral_bonus_email, send_kyc_completion_email, send_withdrawal_confirmation_email,
    send_admin_bonus_email
)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Index route - Landing page
@app.route('/')
def index():
    # Get base URL for referral links
    base_url = request.url_root.rstrip('/')
    return render_template('index.html', base_url=base_url)

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
        
        # Send welcome email to user
        email_sent = send_welcome_email(username, email, new_user.wallet_address)
        
        if email_sent:
            logging.info(f"Welcome email sent to {email}")
        else:
            logging.warning(f"Failed to send welcome email to {email}")
        
        flash('Account created successfully! You can now log in. Check your email for details.', 'success')
        return redirect(url_for('login'))
    
    # Get base URL for referral links
    base_url = request.url_root.rstrip('/')
    return render_template('signup.html', base_url=base_url)

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
    
    # Get base URL for referral links
    base_url = request.url_root.rstrip('/')
    return render_template('login.html', base_url=base_url)

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
    
    # Get base URL for referral links
    base_url = request.url_root.rstrip('/')
    return render_template('admin_login.html', base_url=base_url)

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
    
    # Get base URL for referral links
    base_url = request.url_root.rstrip('/')
    
    return render_template(
        'dashboard.html', 
        user=user.to_dict(), 
        transactions=user_transactions,
        referral_count=referral_count,
        base_url=base_url
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
    
    # Get base URL for referral links
    base_url = request.url_root.rstrip('/')
    
    return render_template(
        'profile.html',
        user=user.to_dict(),
        referral_count=referral_count,
        base_url=base_url
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
            # Send transaction email to receiver
            receiver = users[receiver_email]
            email_sent = send_transaction_email(
                receiver.username, 
                receiver_email, 
                user_email, 
                amount, 
                receiver.balance_coins, 
                receiver.balance_usd
            )
            
            if email_sent:
                logging.info(f"Transaction notification email sent to {receiver_email}")
            else:
                logging.warning(f"Failed to send transaction notification email to {receiver_email}")
            
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
            # Send purchase confirmation email
            email_sent = send_purchase_email(
                user.username, 
                user_email, 
                amount, 
                user.balance_coins, 
                user.balance_usd
            )
            
            if email_sent:
                logging.info(f"Purchase confirmation email sent to {user_email}")
            else:
                logging.warning(f"Failed to send purchase confirmation email to {user_email}")
            
            flash('Purchase successful. Check your email for confirmation.', 'success')
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
    
    if result['success']:
        # Send KYC completion confirmation email
        user = users[user_email]
        email_sent = send_kyc_completion_email(user.username, user_email)
        
        if email_sent:
            logging.info(f"KYC completion email sent to {user_email}")
        else:
            logging.warning(f"Failed to send KYC completion email to {user_email}")
    
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
        # Send admin bonus email
        user = users[user_email]
        email_sent = send_admin_bonus_email(
            user.username, 
            user_email, 
            amount, 
            user.balance_coins
        )
        
        if email_sent:
            logging.info(f"Admin bonus notification email sent to {user_email}")
        else:
            logging.warning(f"Failed to send admin bonus notification email to {user_email}")
    
    return jsonify(result)

# Admin - Send Coins to User (API)
@app.route('/api/admin/send-coins', methods=['POST'])
def admin_send_coins():
    if 'user_email' not in session or 'is_admin' not in session:
        return jsonify({"success": False, "message": "Not authorized"}), 401
    
    admin_email = session['user_email']
    if admin_email not in users or not users[admin_email].is_admin:
        return jsonify({"success": False, "message": "Not authorized"}), 401
    
    recipient_email = request.json.get('recipient_email')
    amount = request.json.get('amount')
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({"success": False, "message": "Amount must be greater than 0"})
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid amount"})
    
    # Send coins from admin to user
    result = send_coins(admin_email, recipient_email, amount)
    
    if result['success']:
        # Send transaction email to receiver
        recipient = users[recipient_email]
        email_sent = send_transaction_email(
            recipient.username, 
            recipient_email, 
            admin_email, 
            amount, 
            recipient.balance_coins, 
            recipient.balance_usd
        )
        
        if email_sent:
            logging.info(f"Admin transaction notification email sent to {recipient_email}")
        else:
            logging.warning(f"Failed to send admin transaction notification email to {recipient_email}")
    
    return jsonify(result)

# Check balance visibility (API)
@app.route('/api/balance/check-visibility')
def check_balance_visibility():
    balance_hidden = session.get('balance_hidden', False)
    
    return jsonify({
        "balance_hidden": balance_hidden
    })
