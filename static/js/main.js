/**
 * OMINA Coin Wallet - Main JavaScript
 * Handles general functionality across the application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Toggle for dark/light mode
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        // Check if user previously set a preference
        const currentTheme = localStorage.getItem('theme') || 'light';
        if (currentTheme === 'dark') {
            document.body.classList.add('dark-mode');
            themeToggle.checked = true;
        }

        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light');
            }
        });
    }
    
    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-button');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            const tempInput = document.createElement('input');
            tempInput.value = textToCopy;
            document.body.appendChild(tempInput);
            tempInput.select();
            document.execCommand('copy');
            document.body.removeChild(tempInput);
            
            // Show toast notification
            showToast('Copied to clipboard!', 'success');
            
            // Change button text temporarily
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => {
                this.innerHTML = originalText;
            }, 2000);
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Balance visibility toggle
    const balanceToggle = document.getElementById('balance-toggle');
    if (balanceToggle) {
        // Check current visibility state from server
        fetch('/api/balance/check-visibility')
            .then(response => response.json())
            .then(data => {
                const balanceElements = document.querySelectorAll('.balance-value');
                if (data.balance_hidden) {
                    balanceElements.forEach(el => el.classList.add('balance-hidden'));
                    balanceToggle.innerHTML = '<i class="fas fa-eye"></i> Show Balance';
                } else {
                    balanceElements.forEach(el => el.classList.remove('balance-hidden'));
                    balanceToggle.innerHTML = '<i class="fas fa-eye-slash"></i> Hide Balance';
                }
            });

        balanceToggle.addEventListener('click', function() {
            fetch('/api/balance/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                const balanceElements = document.querySelectorAll('.balance-value');
                if (data.balance_hidden) {
                    balanceElements.forEach(el => el.classList.add('balance-hidden'));
                    this.innerHTML = '<i class="fas fa-eye"></i> Show Balance';
                } else {
                    balanceElements.forEach(el => el.classList.remove('balance-hidden'));
                    this.innerHTML = '<i class="fas fa-eye-slash"></i> Hide Balance';
                }
            });
        });
    }
    

    // Toast notification function
    window.showToast = function(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            const newContainer = document.createElement('div');
            newContainer.className = 'toast-container';
            document.body.appendChild(newContainer);
        }
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span class="toast-close">&times;</span>
            <div>${message}</div>
        `;
        
        document.querySelector('.toast-container').appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 5000);
        
        // Close button functionality
        toast.querySelector('.toast-close').addEventListener('click', function() {
            toast.style.opacity = '0';
            setTimeout(() => {
                toast.remove();
            }, 300);
        });
    }
    
    // Admin section functionality
    const confirmDepositBtns = document.querySelectorAll('.confirm-deposit-btn');
    if (confirmDepositBtns.length > 0) {
        confirmDepositBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const userEmail = this.getAttribute('data-user');
                confirmDeposit(userEmail, this);
            });
        });
    }
    
    const completeKycBtns = document.querySelectorAll('.complete-kyc-btn');
    if (completeKycBtns.length > 0) {
        completeKycBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const userEmail = this.getAttribute('data-user');
                completeKyc(userEmail, this);
            });
        });
    }
    
    const sendBonusBtns = document.querySelectorAll('.send-bonus-btn');
    if (sendBonusBtns.length > 0) {
        sendBonusBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const userEmail = this.getAttribute('data-user');
                const bonusAmount = prompt('Enter bonus amount:', '20');
                
                if (bonusAmount !== null && !isNaN(bonusAmount) && parseFloat(bonusAmount) > 0) {
                    sendBonus(userEmail, parseFloat(bonusAmount), this);
                } else if (bonusAmount !== null) {
                    showToast('Please enter a valid amount', 'error');
                }
            });
        });
    }
    
    function confirmDeposit(userEmail, button) {
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        
        fetch('/api/admin/confirm-deposit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_email: userEmail })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Deposit confirmed and withdrawals unlocked!', 'success');
                // Update button state
                button.classList.remove('btn-primary');
                button.classList.add('btn-success');
                button.innerHTML = '<i class="fas fa-check"></i> Confirmed';
                button.disabled = true;
            } else {
                showToast(data.message || 'Error confirming deposit', 'error');
                button.disabled = false;
                button.innerHTML = originalText;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Network error. Please try again.', 'error');
            button.disabled = false;
            button.innerHTML = originalText;
        });
    }
    
    function completeKyc(userEmail, button) {
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        
        fetch('/api/admin/complete-kyc', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_email: userEmail })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('KYC verification completed!', 'success');
                // Update button state
                button.classList.remove('btn-warning');
                button.classList.add('btn-success');
                button.innerHTML = '<i class="fas fa-check"></i> Verified';
                button.disabled = true;
            } else {
                showToast(data.message || 'Error completing KYC', 'error');
                button.disabled = false;
                button.innerHTML = originalText;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Network error. Please try again.', 'error');
            button.disabled = false;
            button.innerHTML = originalText;
        });
    }
    
    function sendBonus(userEmail, amount, button) {
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sending...';
        
        fetch('/api/admin/apply-bonus', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                user_email: userEmail,
                amount: amount
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(`Bonus of ${amount} OMINA Coins sent successfully!`, 'success');
                button.disabled = false;
                button.innerHTML = originalText;
            } else {
                showToast(data.message || 'Error sending bonus', 'error');
                button.disabled = false;
                button.innerHTML = originalText;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Network error. Please try again.', 'error');
            button.disabled = false;
            button.innerHTML = originalText;
        });
    }
});