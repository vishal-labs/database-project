let restaurants = [];
let currentRestaurantItems = {};
let searchTimeout = null;

async function loadRestaurants() {
    const container = document.getElementById('restaurants');
    container.innerHTML = '<div style="text-align: center; padding: 40px;"><p style="color: #686b78;">Loading restaurants...</p></div>';
    
    try {
        const response = await fetch('/api/restaurants');
        const data = await response.json();
        
        if (data.success) {
            restaurants = data.restaurants;
            if (restaurants.length === 0) {
                container.innerHTML = '<div style="text-align: center; padding: 40px;"><p style="color: #686b78;">No restaurants available.</p></div>';
            } else {
                displayRestaurants();
            }
        } else {
            container.innerHTML = '<div style="text-align: center; padding: 40px;"><p style="color: #dc3545;">❌ Error loading restaurants: ' + (data.message || 'Unknown error') + '</p></div>';
        }
    } catch (error) {
        container.innerHTML = '<div style="text-align: center; padding: 40px;"><p style="color: #dc3545;">❌ Error: ' + error.message + '</p></div>';
    }
}

async function loadRestaurantItems(restaurantId) {
    if (currentRestaurantItems[restaurantId]) {
        return currentRestaurantItems[restaurantId];
    }
    
    const itemsContainer = document.getElementById(`items-${restaurantId}`);
    if (itemsContainer) {
        itemsContainer.innerHTML = '<p style="padding: 20px; text-align: center; color: #93959f;">Loading items...</p>';
    }
    
    try {
        const response = await fetch(`/api/restaurants/${restaurantId}/items`);
        const data = await response.json();
        
        if (data.success) {
            currentRestaurantItems[restaurantId] = data.items;
            return data.items;
        }
    } catch (error) {
        console.error('Error loading items:', error);
    }
    return [];
}

function displayRestaurants() {
    const container = document.getElementById('restaurants');
    
    if (restaurants.length === 0) {
        container.innerHTML = '<p>No restaurants available</p>';
        return;
    }
    
    container.innerHTML = restaurants.map(restaurant => `
        <div class="restaurant-card">
            <div class="restaurant-header">
                <h3>${restaurant.name}</h3>
                <p>${restaurant.description || 'Delicious food awaits'}</p>
            </div>
            <div class="items-list" id="items-${restaurant.id}">
                <p style="padding: 20px; text-align: center; color: #93959f;">Loading items...</p>
            </div>
        </div>
    `).join('');
    
    restaurants.forEach(restaurant => {
        loadRestaurantItems(restaurant.id).then(items => {
            displayItems(restaurant.id, items);
        });
    });
}

function displayItems(restaurantId, items) {
    const itemsContainer = document.getElementById(`items-${restaurantId}`);
    if (!itemsContainer) return;
    
    if (items.length === 0) {
        itemsContainer.innerHTML = '<p style="padding: 20px; text-align: center; color: #93959f;">No items available</p>';
        return;
    }
    
    itemsContainer.innerHTML = items.map(item => `
        <div class="item-card">
            <div class="item-info">
                <h4>${item.name}</h4>
                <p>${item.description || ''}</p>
                <span class="item-price">₹${parseFloat(item.price).toFixed(2)}</span>
            </div>
            <div class="item-actions">
                <button class="add-to-cart-btn" onclick="addToCart(${item.id}, '${item.name.replace(/'/g, "\\'")}')">
                    ADD
                </button>
            </div>
        </div>
    `).join('');
}

async function addToCart(itemId, itemName) {
    const user = loadUserInfo();
    if (!user) {
        showNotification('❌ Please login to add items to cart', 'error');
        return;
    }

    const btn = event.target;
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'ADDING...';
    
    try {
        const response = await fetch('/api/cart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId, quantity: 1, user_id: user.id })
        });
        
        const data = await response.json();
        
        if (data.success) {
            btn.textContent = '✓ ADDED';
            btn.style.backgroundColor = '#28a745';
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.backgroundColor = '';
                btn.disabled = false;
            }, 2000);
            showNotification('✅ ' + itemName + ' added to cart!', 'success');
        } else {
            btn.textContent = originalText;
            btn.disabled = false;
            showNotification('❌ Error: ' + (data.message || 'Failed to add item'), 'error');
        }
    } catch (error) {
        btn.textContent = originalText;
        btn.disabled = false;
        showNotification('❌ Error: ' + error.message, 'error');
    }
}

// ============================================================================
// SEARCH
// ============================================================================

function handleSearch(query) {
    clearTimeout(searchTimeout);
    const searchResults = document.getElementById('searchResults');
    const restaurantsGrid = document.getElementById('restaurants');

    if (!query.trim()) {
        searchResults.style.display = 'none';
        restaurantsGrid.style.display = '';
        return;
    }

    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query.trim())}`);
            const data = await response.json();

            if (data.success && data.items.length > 0) {
                restaurantsGrid.style.display = 'none';
                searchResults.style.display = 'block';
                searchResults.innerHTML = `
                    <p style="color: #686b78; margin-bottom: 15px;">${data.items.length} result(s) for "${query}"</p>
                    ${data.items.map(item => `
                        <div class="search-result-card">
                            <div class="item-info">
                                <h4>${item.name}</h4>
                                <p>${item.description || ''}</p>
                                <p style="color: #93959f; font-size: 12px;">${item.restaurant_name}</p>
                                <span class="item-price">₹${parseFloat(item.price).toFixed(2)}</span>
                            </div>
                            <div class="item-actions">
                                <button class="add-to-cart-btn" onclick="addToCart(${item.id}, '${item.name.replace(/'/g, "\\'")}')">ADD</button>
                            </div>
                        </div>
                    `).join('')}
                `;
            } else {
                restaurantsGrid.style.display = 'none';
                searchResults.style.display = 'block';
                searchResults.innerHTML = `<p style="color: #686b78; text-align: center; padding: 40px;">No items found for "${query}"</p>`;
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }, 300);
}

// ============================================================================
// NOTIFICATION
// ============================================================================

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

// Load restaurants on page load
loadRestaurants();
