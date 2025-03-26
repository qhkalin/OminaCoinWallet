/**
 * OMINA Coin Wallet - Admin Dashboard JavaScript
 * Handles functionality specific to the admin dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Helper function to show toast notifications
    function showToast(message, type = 'info') {
        // Check if we already have a toast container
        let toastContainer = document.querySelector('.toast-container');
        
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        // Create toast content
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Add toast to container
        toastContainer.appendChild(toastEl);
        
        // Initialize and show toast
        const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 5000 });
        toast.show();
        
        // Remove toast after it's hidden
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastEl.remove();
        });
    }
    // Initialize user statistics chart
    const userStatsChart = document.getElementById('userStatsChart');
    
    if (userStatsChart) {
        const ctx = userStatsChart.getContext('2d');
        
        // Get user data from the page
        const userElements = document.querySelectorAll('.user-card');
        const usernames = [];
        const balances = [];
        const referralCounts = [];
        
        userElements.forEach(userEl => {
            usernames.push(userEl.getAttribute('data-username'));
            balances.push(parseFloat(userEl.getAttribute('data-balance')));
            referralCounts.push(parseInt(userEl.getAttribute('data-referrals')));
        });
        
        // Create chart
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: usernames,
                datasets: [
                    {
                        label: 'Balance (USD)',
                        data: balances,
                        backgroundColor: 'rgba(58, 123, 213, 0.7)',
                        borderColor: '#3a7bd5',
                        borderWidth: 1
                    },
                    {
                        label: 'Referrals',
                        data: referralCounts,
                        backgroundColor: 'rgba(255, 159, 67, 0.7)',
                        borderColor: '#ff9f43',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                    }
                }
            }
        });
    }
    
    // Search functionality for users
    const userSearchInput = document.getElementById('user-search');
    
    if (userSearchInput) {
        userSearchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const userCards = document.querySelectorAll('.user-card');
            
            userCards.forEach(card => {
                const username = card.getAttribute('data-username').toLowerCase();
                const email = card.getAttribute('data-email').toLowerCase();
                const wallet = card.getAttribute('data-wallet').toLowerCase();
                
                if (username.includes(searchTerm) || email.includes(searchTerm) || wallet.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Filter users by referral count
    const filterReferralsBtn = document.getElementById('filter-referrals');
    
    if (filterReferralsBtn) {
        filterReferralsBtn.addEventListener('click', function() {
            const minReferrals = prompt('Filter users with at least how many referrals?', '10');
            
            if (minReferrals !== null && !isNaN(minReferrals)) {
                const threshold = parseInt(minReferrals);
                const userCards = document.querySelectorAll('.user-card');
                
                userCards.forEach(card => {
                    const referrals = parseInt(card.getAttribute('data-referrals'));
                    
                    if (referrals >= threshold) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
                
                // Update filter button text
                this.textContent = `Referrals ≥ ${threshold}`;
                
                // Add reset button if it doesn't exist
                if (!document.getElementById('reset-filter')) {
                    const resetBtn = document.createElement('button');
                    resetBtn.id = 'reset-filter';
                    resetBtn.className = 'btn btn-sm btn-outline-secondary ms-2';
                    resetBtn.textContent = 'Reset Filter';
                    resetBtn.addEventListener('click', function() {
                        userCards.forEach(card => {
                            card.style.display = 'block';
                        });
                        filterReferralsBtn.textContent = 'Filter by Referrals';
                        this.remove();
                    });
                    
                    filterReferralsBtn.parentNode.appendChild(resetBtn);
                }
            }
        });
    }
    
    // Mass action buttons
    const massActionBtns = document.querySelectorAll('.mass-action-btn');
    
    if (massActionBtns.length > 0) {
        massActionBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const action = this.getAttribute('data-action');
                const selectedUsers = getSelectedUsers();
                
                if (selectedUsers.length === 0) {
                    showToast('Please select at least one user', 'warning');
                    return;
                }
                
                switch(action) {
                    case 'confirm-deposits':
                        confirmDepositsForUsers(selectedUsers);
                        break;
                    case 'complete-kyc':
                        completeKycForUsers(selectedUsers);
                        break;
                    case 'send-bonus':
                        const bonusAmount = prompt('Enter bonus amount for all selected users:', '20');
                        if (bonusAmount !== null && !isNaN(bonusAmount) && parseFloat(bonusAmount) > 0) {
                            sendBonusToUsers(selectedUsers, parseFloat(bonusAmount));
                        }
                        break;
                }
            });
        });
    }
    
    // Get selected users
    function getSelectedUsers() {
        const selectedCheckboxes = document.querySelectorAll('.user-select:checked');
        return Array.from(selectedCheckboxes).map(checkbox => checkbox.value);
    }
    
    // Select all users checkbox
    const selectAllCheckbox = document.getElementById('select-all-users');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const userCheckboxes = document.querySelectorAll('.user-select');
            userCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
    
    // Confirm deposits for multiple users
    function confirmDepositsForUsers(userEmails) {
        showToast(`Processing deposit confirmation for ${userEmails.length} users...`, 'info');
        
        let processed = 0;
        let successful = 0;
        
        userEmails.forEach(email => {
            fetch('/api/admin/confirm-deposit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_email: email })
            })
            .then(response => response.json())
            .then(data => {
                processed++;
                if (data.success) {
                    successful++;
                    // Update UI for the specific user
                    const depositBtn = document.querySelector(`.confirm-deposit-btn[data-user="${email}"]`);
                    if (depositBtn) {
                        depositBtn.classList.remove('btn-primary');
                        depositBtn.classList.add('btn-success');
                        depositBtn.innerHTML = '<i class="fas fa-check"></i> Confirmed';
                        depositBtn.disabled = true;
                    }
                }
                
                // If all requests have been processed, show final status
                if (processed === userEmails.length) {
                    showToast(`Successfully confirmed deposits for ${successful} of ${userEmails.length} users`, 'success');
                }
            })
            .catch(error => {
                processed++;
                console.error('Error:', error);
                
                // If all requests have been processed, show final status
                if (processed === userEmails.length) {
                    showToast(`Successfully confirmed deposits for ${successful} of ${userEmails.length} users`, 'success');
                }
            });
        });
    }
    
    // Complete KYC for multiple users
    function completeKycForUsers(userEmails) {
        showToast(`Processing KYC verification for ${userEmails.length} users...`, 'info');
        
        let processed = 0;
        let successful = 0;
        
        userEmails.forEach(email => {
            fetch('/api/admin/complete-kyc', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_email: email })
            })
            .then(response => response.json())
            .then(data => {
                processed++;
                if (data.success) {
                    successful++;
                    // Update UI for the specific user
                    const kycBtn = document.querySelector(`.complete-kyc-btn[data-user="${email}"]`);
                    if (kycBtn) {
                        kycBtn.classList.remove('btn-warning');
                        kycBtn.classList.add('btn-success');
                        kycBtn.innerHTML = '<i class="fas fa-check"></i> Verified';
                        kycBtn.disabled = true;
                    }
                }
                
                // If all requests have been processed, show final status
                if (processed === userEmails.length) {
                    showToast(`Successfully completed KYC for ${successful} of ${userEmails.length} users`, 'success');
                }
            })
            .catch(error => {
                processed++;
                console.error('Error:', error);
                
                // If all requests have been processed, show final status
                if (processed === userEmails.length) {
                    showToast(`Successfully completed KYC for ${successful} of ${userEmails.length} users`, 'success');
                }
            });
        });
    }
    
    // Send bonus to multiple users
    function sendBonusToUsers(userEmails, amount) {
        showToast(`Sending ${amount} OMINA Coins bonus to ${userEmails.length} users...`, 'info');
        
        let processed = 0;
        let successful = 0;
        
        userEmails.forEach(email => {
            fetch('/api/admin/apply-bonus', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    user_email: email,
                    amount: amount
                })
            })
            .then(response => response.json())
            .then(data => {
                processed++;
                if (data.success) {
                    successful++;
                }
                
                // If all requests have been processed, show final status
                if (processed === userEmails.length) {
                    showToast(`Successfully sent ${amount} OMINA Coins to ${successful} of ${userEmails.length} users`, 'success');
                }
            })
            .catch(error => {
                processed++;
                console.error('Error:', error);
                
                // If all requests have been processed, show final status
                if (processed === userEmails.length) {
                    showToast(`Successfully sent ${amount} OMINA Coins to ${successful} of ${userEmails.length} users`, 'success');
                }
            });
        });
    }
    
    // Handle wallet management button click
    const manageWalletBtns = document.querySelectorAll('.manage-wallet-btn');
    if (manageWalletBtns.length > 0) {
        manageWalletBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const userEmail = this.getAttribute('data-user');
                const walletAddress = this.getAttribute('data-wallet');
                
                // Get parent container for user data
                const userCard = this.closest('.user-card');
                const coinBalance = userCard.querySelector('.badge.bg-primary').textContent.split(' ')[0];
                const usdBalance = userCard.querySelector('.badge.bg-success').textContent.replace('$', '');
                
                // Set modal data
                document.getElementById('wallet-user-email').textContent = userEmail;
                document.getElementById('wallet-address').textContent = walletAddress;
                document.getElementById('wallet-coin-balance').textContent = coinBalance + ' OMINA';
                document.getElementById('wallet-usd-balance').textContent = '$' + usdBalance;
                
                // Show modal
                const walletModal = new bootstrap.Modal(document.getElementById('walletManagementModal'));
                walletModal.show();
            });
        });
    }
    
    // Handle direct send button click
    const directSendBtn = document.getElementById('direct-send-btn');
    if (directSendBtn) {
        directSendBtn.addEventListener('click', function() {
            const userEmail = document.getElementById('wallet-user-email').textContent;
            const walletModal = bootstrap.Modal.getInstance(document.getElementById('walletManagementModal'));
            walletModal.hide();
            
            // Set up the send coins modal
            document.getElementById('recipient-info').textContent = userEmail;
            document.getElementById('recipient-email').value = userEmail;
            
            // Show send coins modal
            const sendModal = new bootstrap.Modal(document.getElementById('sendCoinsAdminModal'));
            sendModal.show();
        });
    }
    
    // Handle modal send bonus button click
    const modalSendBonusBtn = document.getElementById('modal-send-bonus-btn');
    if (modalSendBonusBtn) {
        modalSendBonusBtn.addEventListener('click', function() {
            const userEmail = document.getElementById('wallet-user-email').textContent;
            const walletModal = bootstrap.Modal.getInstance(document.getElementById('walletManagementModal'));
            walletModal.hide();
            
            // Set up the bonus modal
            document.getElementById('bonus-user-email').textContent = userEmail;
            document.getElementById('bonus-user-email-input').value = userEmail;
            
            // Show bonus modal
            const bonusModal = new bootstrap.Modal(document.getElementById('sendBonusModal'));
            bonusModal.show();
        });
    }
    
    // Handle admin send confirm button click
    const adminSendConfirmBtn = document.getElementById('admin-send-confirm');
    if (adminSendConfirmBtn) {
        adminSendConfirmBtn.addEventListener('click', function() {
            const recipientEmail = document.getElementById('recipient-email').value;
            const amount = document.getElementById('admin-send-amount').value;
            
            if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
                showToast('Please enter a valid amount', 'warning');
                return;
            }
            
            // Send request to server
            fetch('/api/admin/send-coins', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    recipient_email: recipientEmail,
                    amount: parseFloat(amount)
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(`Successfully sent ${amount} OMINA Coins to ${recipientEmail}`, 'success');
                    
                    // Close modal
                    const sendModal = bootstrap.Modal.getInstance(document.getElementById('sendCoinsAdminModal'));
                    sendModal.hide();
                    
                    // Reset form
                    document.getElementById('admin-send-form').reset();
                } else {
                    showToast(data.message || 'Failed to send coins', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('An error occurred while sending coins', 'danger');
            });
        });
    }
    
    // Handle send bonus confirm button click  
    const sendBonusConfirmBtn = document.getElementById('send-bonus-confirm');
    if (sendBonusConfirmBtn) {
        sendBonusConfirmBtn.addEventListener('click', function() {
            const userEmail = document.getElementById('bonus-user-email-input').value;
            const amount = document.getElementById('bonus-amount').value;
            
            if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
                showToast('Please enter a valid amount', 'warning');
                return;
            }
            
            // Send request to server
            fetch('/api/admin/apply-bonus', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    user_email: userEmail,
                    amount: parseFloat(amount)
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast(`Successfully sent ${amount} OMINA Coins bonus to ${userEmail}`, 'success');
                    
                    // Close modal
                    const bonusModal = bootstrap.Modal.getInstance(document.getElementById('sendBonusModal'));
                    bonusModal.hide();
                    
                    // Reset form
                    document.getElementById('bonus-form').reset();
                } else {
                    showToast(data.message || 'Failed to send bonus', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('An error occurred while sending bonus', 'danger');
            });
        });
    }
    
    // Copy wallet address button
    const copyWalletBtn = document.querySelector('.copy-wallet-btn');
    if (copyWalletBtn) {
        copyWalletBtn.addEventListener('click', function() {
            const walletAddress = document.getElementById('wallet-address').textContent;
            navigator.clipboard.writeText(walletAddress);
            showToast('Wallet address copied to clipboard', 'success');
        });
    }
});
