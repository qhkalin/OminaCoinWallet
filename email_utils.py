import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USERNAME = "exesoftware010@gmail.com"
SMTP_PASSWORD = "lmgz etkx gude udar"
SENDER_NAME = "OMINA Coin Wallet"

def send_email(recipient_email, subject, html_content):
    """Send an email to a user using the configured SMTP server.
    
    Args:
        recipient_email (str): The recipient's email address
        subject (str): Email subject
        html_content (str): HTML content of the email
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f"{SENDER_NAME} <{SMTP_USERNAME}>"
        message['To'] = recipient_email
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)
        
        # Send email using SSL
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, recipient_email, message.as_string())
            
        logging.info(f"Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False

def send_welcome_email(username, email, wallet_address):
    """Send a welcome email to a newly registered user.
    
    Args:
        username (str): The user's username
        email (str): The user's email address
        wallet_address (str): The user's wallet address
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = "Welcome to OMINA Wallet – Your Crypto Journey Begins!"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://ominacoin.com/static/images/logo.svg" alt="OMINA Coin Wallet Logo" style="width: 200px;">
        </div>
        
        <h2 style="color: #4a6ee0;">Welcome to OMINA Coin Wallet! 🎉</h2>
        
        <p>Dear {username},</p>
        
        <p>Congratulations! Your OMINA Wallet has been created successfully. We're excited to have you join our community of cryptocurrency enthusiasts.</p>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #4a6ee0;">Your Wallet Details</h3>
            <p><strong>Wallet Address:</strong> {wallet_address}</p>
            <p><strong>Starting Balance:</strong> 12 OMINA Coins ($12.00)</p>
        </div>
        
        <p>You can access your wallet by logging in to your account. Start referring users and earning rewards now!</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://ominacoin.com/login" style="background-color: #4a6ee0; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Log Into Your Wallet</a>
        </div>
        
        <p>If you have any questions or need assistance, feel free to contact our support team at support@ominacoin.com.</p>
        
        <p>Best regards,<br>The OMINA Coin Wallet Team</p>
    </div>
    """
    
    return send_email(email, subject, html_content)

def send_transaction_email(username, email, sender_email, amount, coin_balance, usd_balance):
    """Send an email notifying a user they've received coins.
    
    Args:
        username (str): The recipient's username
        email (str): The recipient's email address
        sender_email (str): The sender's email address
        amount (float): The amount of coins sent
        coin_balance (float): The updated coin balance
        usd_balance (float): The updated USD balance
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = "You've received OMINA Coins!"
    
    # Format amounts with 2 decimal places
    amount_formatted = f"{amount:.2f}"
    coin_balance_formatted = f"{coin_balance:.2f}"
    usd_balance_formatted = f"{usd_balance:.2f}"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://ominacoin.com/static/images/logo.svg" alt="OMINA Coin Wallet Logo" style="width: 200px;">
        </div>
        
        <h2 style="color: #4a6ee0;">You've Received OMINA Coins! 💰</h2>
        
        <p>Dear {username},</p>
        
        <p>Great news! You have received {amount_formatted} OMINA Coins from {sender_email}.</p>
        
        <div style="background-color: #28a745; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Transaction Details</h3>
            <p><strong>Amount Received:</strong> {amount_formatted} OMINA Coins</p>
            <p><strong>From:</strong> {sender_email}</p>
            <p><strong>Date & Time:</strong> {get_formatted_date()}</p>
        </div>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #4a6ee0;">Your Updated Balance</h3>
            <p><strong>New Balance:</strong> {coin_balance_formatted} OMINA Coins (${usd_balance_formatted})</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://ominacoin.com/dashboard" style="background-color: #4a6ee0; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Transaction</a>
        </div>
        
        <p>If you have any questions about this transaction, please contact our support team at support@ominacoin.com.</p>
        
        <p>Best regards,<br>The OMINA Coin Wallet Team</p>
    </div>
    """
    
    return send_email(email, subject, html_content)

def send_purchase_email(username, email, amount, coin_balance, usd_balance):
    """Send an email confirming a coin purchase.
    
    Args:
        username (str): The user's username
        email (str): The user's email address
        amount (float): The amount of coins purchased
        coin_balance (float): The updated coin balance
        usd_balance (float): The updated USD balance
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = "You've Purchased OMINA Coins!"
    
    # Format amounts with 2 decimal places
    amount_formatted = f"{amount:.2f}"
    coin_balance_formatted = f"{coin_balance:.2f}"
    usd_balance_formatted = f"{usd_balance:.2f}"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://ominacoin.com/static/images/logo.svg" alt="OMINA Coin Wallet Logo" style="width: 200px;">
        </div>
        
        <h2 style="color: #4a6ee0;">Purchase Confirmation 🛒</h2>
        
        <p>Dear {username},</p>
        
        <p>Your purchase of OMINA Coins has been completed successfully!</p>
        
        <div style="background-color: #4a6ee0; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Purchase Details</h3>
            <p><strong>Amount Purchased:</strong> {amount_formatted} OMINA Coins</p>
            <p><strong>Cost:</strong> ${amount_formatted} USD</p>
            <p><strong>Date & Time:</strong> {get_formatted_date()}</p>
        </div>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #4a6ee0;">Your Updated Balance</h3>
            <p><strong>New Coin Balance:</strong> {coin_balance_formatted} OMINA Coins</p>
            <p><strong>New USD Balance:</strong> ${usd_balance_formatted}</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://ominacoin.com/dashboard" style="background-color: #4a6ee0; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Account</a>
        </div>
        
        <p>If you have any questions about this purchase, please contact our support team at support@ominacoin.com.</p>
        
        <p>Best regards,<br>The OMINA Coin Wallet Team</p>
    </div>
    """
    
    return send_email(email, subject, html_content)

def send_referral_bonus_email(username, email, bonus_amount, total_coins, usd_value):
    """Send an email notifying a user of their referral bonus.
    
    Args:
        username (str): The user's username
        email (str): The user's email address
        bonus_amount (float): The bonus amount in coins
        total_coins (float): The updated total coin balance
        usd_value (float): The USD value of the bonus
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = "Congratulations! You've Earned a Referral Bonus!"
    
    # Format amounts with 2 decimal places
    bonus_formatted = f"{bonus_amount:.2f}"
    usd_formatted = f"{usd_value:.2f}"
    total_formatted = f"{total_coins:.2f}"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://ominacoin.com/static/images/logo.svg" alt="OMINA Coin Wallet Logo" style="width: 200px;">
        </div>
        
        <h2 style="color: #4a6ee0;">Referral Bonus Awarded! 🎁</h2>
        
        <p>Dear {username},</p>
        
        <p>Congratulations! You have successfully referred 10 users to OMINA Coin Wallet and earned a special bonus!</p>
        
        <div style="background-color: #ffc107; color: #333; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Bonus Details</h3>
            <p><strong>Bonus Amount:</strong> {bonus_formatted} OMINA Coins</p>
            <p><strong>USD Value:</strong> ${usd_formatted}</p>
            <p><strong>Referral Count:</strong> 10 successful referrals</p>
        </div>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #4a6ee0;">Your Updated Balance</h3>
            <p><strong>New Balance:</strong> {total_formatted} OMINA Coins</p>
        </div>
        
        <p>Keep referring more users to earn additional bonuses! Your next bonus will be unlocked when you reach 50 referrals.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://ominacoin.com/profile" style="background-color: #4a6ee0; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Your Referrals</a>
        </div>
        
        <p>If you have any questions, please contact our support team at support@ominacoin.com.</p>
        
        <p>Best regards,<br>The OMINA Coin Wallet Team</p>
    </div>
    """
    
    return send_email(email, subject, html_content)

def send_kyc_completion_email(username, email):
    """Send an email notifying a user their KYC has been verified.
    
    Args:
        username (str): The user's username
        email (str): The user's email address
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = "Your KYC Verification is Complete!"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://ominacoin.com/static/images/logo.svg" alt="OMINA Coin Wallet Logo" style="width: 200px;">
        </div>
        
        <h2 style="color: #4a6ee0;">KYC Verification Complete! ✅</h2>
        
        <p>Dear {username},</p>
        
        <p>Great news! Your Know Your Customer (KYC) verification has been successfully completed and approved.</p>
        
        <div style="background-color: #28a745; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Verification Status</h3>
            <p><strong>Status:</strong> Approved</p>
            <p><strong>Date Completed:</strong> {get_formatted_date()}</p>
        </div>
        
        <p>With KYC verification complete, you now have access to all features of your OMINA Coin Wallet, including:</p>
        
        <ul style="margin: 20px 0; padding-left: 20px;">
            <li>Unlimited withdrawals</li>
            <li>Higher transaction limits</li>
            <li>Enhanced account security</li>
        </ul>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://ominacoin.com/dashboard" style="background-color: #4a6ee0; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Access Your Wallet</a>
        </div>
        
        <p>If you have any questions or need assistance, please don't hesitate to contact our support team at support@ominacoin.com.</p>
        
        <p>Best regards,<br>The OMINA Coin Wallet Team</p>
    </div>
    """
    
    return send_email(email, subject, html_content)

def send_withdrawal_confirmation_email(username, email, amount, wallet_address):
    """Send an email confirming a withdrawal.
    
    Args:
        username (str): The user's username
        email (str): The user's email address
        amount (float): The amount being withdrawn
        wallet_address (str): The destination wallet address
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = "Withdrawal Confirmation - OMINA Coin Wallet"
    
    # Format amount with 2 decimal places
    amount_formatted = f"{amount:.2f}"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://ominacoin.com/static/images/logo.svg" alt="OMINA Coin Wallet Logo" style="width: 200px;">
        </div>
        
        <h2 style="color: #4a6ee0;">Withdrawal Request Confirmed</h2>
        
        <p>Dear {username},</p>
        
        <p>We are processing your withdrawal request for {amount_formatted} OMINA Coins.</p>
        
        <div style="background-color: #17a2b8; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Withdrawal Details</h3>
            <p><strong>Amount:</strong> {amount_formatted} OMINA Coins</p>
            <p><strong>Destination Address:</strong> {wallet_address}</p>
            <p><strong>Request Date:</strong> {get_formatted_date()}</p>
            <p><strong>Status:</strong> Processing</p>
        </div>
        
        <p>Your withdrawal request is being processed and should be completed within 24 hours. You will receive a confirmation email once the transaction is complete.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://ominacoin.com/dashboard" style="background-color: #4a6ee0; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Transaction</a>
        </div>
        
        <p>If you did not request this withdrawal or have any questions, please contact our support team immediately at support@ominacoin.com.</p>
        
        <p>Best regards,<br>The OMINA Coin Wallet Team</p>
    </div>
    """
    
    return send_email(email, subject, html_content)

def send_admin_bonus_email(username, email, bonus_amount, total_balance):
    """Send an email notifying a user of an admin bonus.
    
    Args:
        username (str): The user's username
        email (str): The user's email address
        bonus_amount (float): The bonus amount in coins
        total_balance (float): The updated total balance
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = "You've Received an Admin Bonus!"
    
    # Format amounts with 2 decimal places
    bonus_formatted = f"{bonus_amount:.2f}"
    total_formatted = f"{total_balance:.2f}"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://ominacoin.com/static/images/logo.svg" alt="OMINA Coin Wallet Logo" style="width: 200px;">
        </div>
        
        <h2 style="color: #4a6ee0;">Admin Bonus Awarded! 🎁</h2>
        
        <p>Dear {username},</p>
        
        <p>Good news! You have received a special bonus from the OMINA Coin Wallet admin team.</p>
        
        <div style="background-color: #6f42c1; color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Bonus Details</h3>
            <p><strong>Bonus Amount:</strong> {bonus_formatted} OMINA Coins</p>
            <p><strong>Date Awarded:</strong> {get_formatted_date()}</p>
        </div>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #4a6ee0;">Your Updated Balance</h3>
            <p><strong>New Balance:</strong> {total_formatted} OMINA Coins</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="https://ominacoin.com/dashboard" style="background-color: #4a6ee0; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Your Wallet</a>
        </div>
        
        <p>Thank you for being a valued member of the OMINA Coin Wallet community!</p>
        
        <p>Best regards,<br>The OMINA Coin Wallet Team</p>
    </div>
    """
    
    return send_email(email, subject, html_content)

def get_formatted_date():
    """Get the current date and time formatted for emails.
    
    Returns:
        str: Formatted date and time string
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")