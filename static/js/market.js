
// Market price update functionality
function updateMarketPrice() {
  fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd')
    .then(response => response.json())
    .then(data => {
      // Using Bitcoin as a reference for demonstration
      const price = data.bitcoin.usd;
      const priceElement = document.getElementById('current-price');
      if (priceElement) {
        priceElement.textContent = `$${price.toLocaleString()}`;
      }
    })
    .catch(console.error);
}

// Update price every 60 seconds
updateMarketPrice();
setInterval(updateMarketPrice, 60000);
