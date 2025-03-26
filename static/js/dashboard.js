/**
 * OMINA Coin Wallet - Dashboard JavaScript
 * Handles functionality specific to the user dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize balance chart if it exists
    const balanceChartElement = document.getElementById('balanceChart');
    let balanceChart;
    
    if (balanceChartElement) {
        const ctx = balanceChartElement.getContext('2d');
        
        // Get initial balance data
        const coinBalance = parseFloat(document.getElementById('coin-balance').textContent);
        const usdBalance = parseFloat(document.getElementById('usd-balance').textContent);
        
        // Create initial chart data
        const chartData = {
            labels: ['Today'],
            datasets: [
                {
                    label: 'OMINA Coins',
                    data: [coinBalance],
                    borderColor: '#3a7bd5',
                    backgroundColor: 'rgba(58, 123, 213, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'USD Value',
                    data: [usdBalance],
                    borderColor: '#00b894',
                    backgroundColor: 'rgba(0, 184, 148, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }
            ]
        };
        
        // Chart configuration
        const chartConfig = {
            type: 'line',
            data: chartData,
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
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('en-US', {
                                        style: 'decimal',
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2
                                    }).format(context.parsed.y);
                                }
                                return label;
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        };
        
        // Create chart
        balanceChart = new Chart(ctx, chartConfig);
        
        // Simulate data for demo purposes
        // In a real application, this would come from actual transaction history
        simulateHistoricalData(balanceChart);
    }
    
    // Simulate adding historical data points
    function simulateHistoricalData(chart) {
        const dates = [];
        const today = new Date();
        
        // Generate dates for the last 7 days
        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(today.getDate() - i);
            dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }
        
        // Initial balance values
        const initialCoinBalance = parseFloat(document.getElementById('coin-balance').textContent);
        const initialUsdBalance = parseFloat(document.getElementById('usd-balance').textContent);
        
        // Generate random historical data that gradually increases to current balance
        const coinData = [];
        const usdData = [];
        
        for (let i = 0; i < 6; i++) {
            // Start with a small balance and gradually increase
            const factor = i / 6;
            coinData.push(initialCoinBalance * factor * (0.9 + Math.random() * 0.2));
            usdData.push(initialUsdBalance * factor * (0.9 + Math.random() * 0.2));
        }
        
        // Add current balance as the last point
        coinData.push(initialCoinBalance);
        usdData.push(initialUsdBalance);
        
        // Update chart
        chart.data.labels = dates;
        chart.data.datasets[0].data = coinData;
        chart.data.datasets[1].data = usdData;
        chart.update();
    }
    
    // Copy referral link functionality
    const referralLinkElement = document.getElementById('referral-link');
    const copyReferralBtn = document.getElementById('copy-referral');
    
    if (referralLinkElement && copyReferralBtn) {
        copyReferralBtn.addEventListener('click', function() {
            const tempInput = document.createElement('input');
            tempInput.value = referralLinkElement.textContent;
            document.body.appendChild(tempInput);
            tempInput.select();
            document.execCommand('copy');
            document.body.removeChild(tempInput);
            
            // Update button text
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => {
                this.innerHTML = originalText;
            }, 2000);
            
            // Show toast
            showToast('Referral link copied to clipboard!', 'success');
        });
    }
    
    // Transaction detail modal
    const txButtons = document.querySelectorAll('.view-transaction-btn');
    
    if (txButtons.length > 0) {
        txButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const txId = this.getAttribute('data-tx-id');
                const txType = this.getAttribute('data-tx-type');
                const txAmount = this.getAttribute('data-tx-amount');
                const txDate = this.getAttribute('data-tx-date');
                const txSender = this.getAttribute('data-tx-sender');
                const txReceiver = this.getAttribute('data-tx-receiver');
                
                // Update modal content
                document.getElementById('modal-tx-id').textContent = txId;
                document.getElementById('modal-tx-type').textContent = txType.charAt(0).toUpperCase() + txType.slice(1);
                document.getElementById('modal-tx-amount').textContent = txAmount;
                document.getElementById('modal-tx-date').textContent = txDate;
                document.getElementById('modal-tx-sender').textContent = txSender;
                document.getElementById('modal-tx-receiver').textContent = txReceiver;
                
                // Show modal
                const txModal = new bootstrap.Modal(document.getElementById('transactionDetailModal'));
                txModal.show();
            });
        });
    }
});
