let cartItems = [];

async function loadCart() {
    const container = document.getElementById('cartItems');
    container.innerHTML = '<div style="text-align: center; padding: 40px;"><p style="color: #686b78;">Loading cart...</p></div>';
    
    const user = loadUserInfo();
    if (!user) {
        container.innerHTML = '<div class="empty-cart"><p>Please <a href="/login">login</a> to view your cart</p></div>';
        document.getElementById('checkoutSection').style.display = 'none';
        return;
    }

    try {
        const response = await fetch(`/api/cart?user_id=${user.id}`);
        const data = await response.json();
        
        if (data.success) {
            cartItems = data.cart;
            displayCart();
        } else {
            container.innerHTML = '<div style="text-align: center; padding: 40px;"><p style="color: #dc3545;">❌ Error loading cart: ' + (data.message || 'Unknown error') + '</p></div>';
        }
    } catch (error) {
        container.innerHTML = '<div style="text-align: center; padding: 40px;"><p style="color: #dc3545;">❌ Error: ' + error.message + '</p></div>';
    }
}

function displayCart() {
    const container = document.getElementById('cartItems');
    const checkoutSection = document.getElementById('checkoutSection');
    
    if (cartItems.length === 0) {
        container.innerHTML = '<div class="empty-cart"><p>Your cart is empty</p></div>';
        checkoutSection.style.display = 'none';
        return;
    }
    
    let total = 0;
    container.innerHTML = cartItems.map(item => {
        const itemTotal = parseFloat(item.price) * item.quantity;
        total += itemTotal;
        return `
            <div class="cart-item">
                <div class="cart-item-info">
                    <h4>${item.name}</h4>
                    <p style="color: #93959f; font-size: 12px;">${item.restaurant_name}</p>
                    <p style="color: #686b78; font-size: 13px; margin-top: 5px;">₹${parseFloat(item.price).toFixed(2)} each</p>
                </div>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div class="qty-controls">
                        <button class="qty-btn" onclick="updateQuantity(${item.item_id}, ${item.quantity - 1})">−</button>
                        <span class="qty-value">${item.quantity}</span>
                        <button class="qty-btn" onclick="updateQuantity(${item.item_id}, ${item.quantity + 1})">+</button>
                    </div>
                    <span class="cart-item-price">₹${itemTotal.toFixed(2)}</span>
                    <button class="remove-btn" onclick="removeFromCart(${item.item_id})">
                        Remove
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML += `<div class="total-price">₹${total.toFixed(2)}</div>`;
    checkoutSection.style.display = 'block';
}

async function updateQuantity(itemId, newQuantity) {
    const user = loadUserInfo();
    if (!user) return;

    try {
        if (newQuantity <= 0) {
            // Remove item
            await removeFromCart(itemId);
            return;
        }

        const response = await fetch('/api/cart', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId, quantity: newQuantity, user_id: user.id })
        });
        const data = await response.json();
        if (data.success) {
            loadCart();
        } else {
            showNotification('❌ ' + (data.message || 'Failed to update quantity'), 'error');
        }
    } catch (error) {
        showNotification('❌ Error: ' + error.message, 'error');
    }
}

async function removeFromCart(itemId) {
    const user = loadUserInfo();
    if (!user) return;

    try {
        const response = await fetch('/api/cart', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId, user_id: user.id })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Item removed from cart', 'success');
            loadCart();
        } else {
            showNotification('❌ Error: ' + (data.message || 'Failed to remove item'), 'error');
        }
    } catch (error) {
        showNotification('❌ Error: ' + error.message, 'error');
    }
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${type === 'success' ? '#d4edda' : '#f8d7da'};
        color: ${type === 'success' ? '#155724' : '#721c24'};
        border-radius: 6px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

document.getElementById('checkoutForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const user = loadUserInfo();
    if (!user) {
        alert('Please login to place an order');
        window.location.href = '/login';
        return;
    }
    
    const address = document.getElementById('address').value.trim();
    const messageDiv = document.getElementById('checkoutMessage');
    const submitBtn = document.querySelector('#checkoutForm button[type="submit"]');
    
    messageDiv.textContent = '';
    messageDiv.className = 'message';
    
    if (!address) {
        messageDiv.textContent = '❌ Please enter a delivery address';
        messageDiv.className = 'message error';
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Placing Order...';
    messageDiv.textContent = 'Processing your order...';
    messageDiv.className = 'message info';
    
    try {
        const response = await fetch('/api/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address, user_id: user.id })
        });
        
        const data = await response.json();
        
        if (data.success) {
            messageDiv.textContent = `✅ Order placed successfully! Order ID: ${data.order_id}`;
            messageDiv.className = 'message success';
            document.getElementById('checkoutForm').reset();
            showNotification('✅ Order placed successfully!', 'success');
            setTimeout(() => {
                loadCart();
            }, 2000);
        } else {
            messageDiv.textContent = '❌ ' + (data.message || 'Checkout failed');
            messageDiv.className = 'message error';
            submitBtn.disabled = false;
            submitBtn.textContent = 'Place Order';
        }
    } catch (error) {
        messageDiv.textContent = '❌ Error: ' + error.message;
        messageDiv.className = 'message error';
        submitBtn.disabled = false;
        submitBtn.textContent = 'Place Order';
    }
});

// Load cart on page load
loadCart();
