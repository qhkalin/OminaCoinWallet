/**
 * OMINA Coin Wallet - Admin Dashboard JavaScript
 * Handles functionality specific to the admin dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
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
});
