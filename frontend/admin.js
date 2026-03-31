// Check if user is admin
document.addEventListener('DOMContentLoaded', function() {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
        window.location.href = '/login';
        return;
    }
    
    const user = JSON.parse(userStr);
    if (!user.is_admin) {
        alert('Access denied. Admin privileges required.');
        window.location.href = '/';
        return;
    }
    
    loadRestaurants();
    loadManageRestaurants();
    loadAllOrders();
});

// ============================================================================
// LOAD RESTAURANTS (for dropdown)
// ============================================================================

async function loadRestaurants() {
    try {
        const response = await fetch('/api/restaurants');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('itemRestaurant');
            select.innerHTML = '<option value="">Select Restaurant</option>';
            data.restaurants.forEach(restaurant => {
                const option = document.createElement('option');
                option.value = restaurant.id;
                option.textContent = restaurant.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading restaurants:', error);
    }
}

// ============================================================================
// ADD RESTAURANT
// ============================================================================

document.getElementById('addRestaurantForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const name = document.getElementById('restaurantName').value.trim();
    const description = document.getElementById('restaurantDescription').value.trim();
    const messageDiv = document.getElementById('adminMessage');
    const submitBtn = document.querySelector('#addRestaurantForm button[type="submit"]');
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Adding...';
    messageDiv.textContent = 'Adding restaurant...';
    messageDiv.className = 'message info';
    
    try {
        const response = await fetch('/api/admin/add-restaurant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        });
        
        const data = await response.json();
        
        if (data.success) {
            messageDiv.textContent = '✅ Restaurant added successfully!';
            messageDiv.className = 'message success';
            document.getElementById('addRestaurantForm').reset();
            loadRestaurants();
            loadManageRestaurants();
        } else {
            messageDiv.textContent = '❌ ' + (data.message || 'Failed to add restaurant');
            messageDiv.className = 'message error';
        }
    } catch (error) {
        messageDiv.textContent = '❌ Error: ' + error.message;
        messageDiv.className = 'message error';
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Add Restaurant';
    }
});

// ============================================================================
// ADD MENU ITEM
// ============================================================================

document.getElementById('addItemForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const restaurantId = parseInt(document.getElementById('itemRestaurant').value);
    const name = document.getElementById('itemName').value.trim();
    const description = document.getElementById('itemDescription').value.trim();
    const price = parseFloat(document.getElementById('itemPrice').value);
    const messageDiv = document.getElementById('adminMessage');
    const submitBtn = document.querySelector('#addItemForm button[type="submit"]');
    
    if (!restaurantId) {
        messageDiv.textContent = '❌ Please select a restaurant';
        messageDiv.className = 'message error';
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Adding...';
    messageDiv.textContent = 'Adding menu item...';
    messageDiv.className = 'message info';
    
    try {
        const response = await fetch('/api/admin/add-item', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ restaurant_id: restaurantId, name, description, price })
        });
        
        const data = await response.json();
        
        if (data.success) {
            messageDiv.textContent = '✅ Menu item added successfully!';
            messageDiv.className = 'message success';
            document.getElementById('addItemForm').reset();
            loadManageRestaurants();
        } else {
            messageDiv.textContent = '❌ ' + (data.message || 'Failed to add item');
            messageDiv.className = 'message error';
        }
    } catch (error) {
        messageDiv.textContent = '❌ Error: ' + error.message;
        messageDiv.className = 'message error';
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Add Item';
    }
});

// ============================================================================
// MANAGE RESTAURANTS (list with delete)
// ============================================================================

async function loadManageRestaurants() {
    const container = document.getElementById('manageRestaurants');
    container.innerHTML = '<p style="text-align: center; padding: 20px; color: #686b78;">Loading...</p>';

    try {
        const response = await fetch('/api/restaurants');
        const data = await response.json();

        if (!data.success || data.restaurants.length === 0) {
            container.innerHTML = '<p style="text-align: center; padding: 20px; color: #686b78;">No restaurants found.</p>';
            return;
        }

        let html = '';
        for (const restaurant of data.restaurants) {
            // Fetch items for this restaurant
            const itemsRes = await fetch(`/api/restaurants/${restaurant.id}/items`);
            const itemsData = await itemsRes.json();
            const items = itemsData.success ? itemsData.items : [];

            html += `
                <div class="manage-restaurant-card">
                    <div class="manage-restaurant-header">
                        <div>
                            <strong>${restaurant.name}</strong>
                            <span style="color: #686b78; font-size: 13px; margin-left: 10px;">${restaurant.description || ''}</span>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <button class="rename-btn" onclick="renameRestaurant(${restaurant.id}, '${restaurant.name.replace(/'/g, "\\'")}')">Rename</button>
                            <button class="delete-btn" onclick="deleteRestaurant(${restaurant.id}, '${restaurant.name.replace(/'/g, "\\'")}')">Delete</button>
                        </div>
                    </div>
                    <div class="manage-items-list">
                        ${items.length === 0 ? '<p style="padding: 10px; color: #93959f; font-size: 13px;">No items</p>' : 
                            items.map(item => `
                                <div class="manage-item-row">
                                    <span>${item.name} — ₹${parseFloat(item.price).toFixed(2)}</span>
                                    <button class="delete-btn small" onclick="deleteItem(${item.id}, '${item.name.replace(/'/g, "\\'")}')">Delete</button>
                                </div>
                            `).join('')
                        }
                    </div>
                </div>
            `;
        }
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<p style="text-align: center; padding: 20px; color: #dc3545;">Error loading restaurants.</p>';
        console.error(error);
    }
}

async function deleteRestaurant(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"? This will also delete all its menu items.`)) return;

    const messageDiv = document.getElementById('adminMessage');
    try {
        const response = await fetch(`/api/admin/delete-restaurant/${id}`, { method: 'DELETE' });
        const data = await response.json();

        if (data.success) {
            messageDiv.textContent = '✅ ' + data.message;
            messageDiv.className = 'message success';
            loadRestaurants();
            loadManageRestaurants();
        } else {
            messageDiv.textContent = '❌ ' + (data.message || 'Failed to delete');
            messageDiv.className = 'message error';
        }
    } catch (error) {
        messageDiv.textContent = '❌ Error: ' + error.message;
        messageDiv.className = 'message error';
    }
}

async function renameRestaurant(id, currentName) {
    const newName = prompt(`Rename "${currentName}" to:`, currentName);
    if (!newName || newName.trim() === '' || newName.trim() === currentName) return;

    const messageDiv = document.getElementById('adminMessage');
    try {
        const response = await fetch(`/api/admin/rename-restaurant/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName.trim() })
        });
        const data = await response.json();

        if (data.success) {
            messageDiv.textContent = '✅ ' + data.message;
            messageDiv.className = 'message success';
            loadRestaurants();
            loadManageRestaurants();
        } else {
            messageDiv.textContent = '❌ ' + (data.message || 'Failed to rename');
            messageDiv.className = 'message error';
        }
    } catch (error) {
        messageDiv.textContent = '❌ Error: ' + error.message;
        messageDiv.className = 'message error';
    }
}

async function deleteItem(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    const messageDiv = document.getElementById('adminMessage');
    try {
        const response = await fetch(`/api/admin/delete-item/${id}`, { method: 'DELETE' });
        const data = await response.json();

        if (data.success) {
            messageDiv.textContent = '✅ ' + data.message;
            messageDiv.className = 'message success';
            loadManageRestaurants();
        } else {
            messageDiv.textContent = '❌ ' + (data.message || 'Failed to delete');
            messageDiv.className = 'message error';
        }
    } catch (error) {
        messageDiv.textContent = '❌ Error: ' + error.message;
        messageDiv.className = 'message error';
    }
}

// ============================================================================
// MANAGE ORDERS (view all + status update)
// ============================================================================

async function loadAllOrders() {
    const container = document.getElementById('manageOrders');
    container.innerHTML = '<p style="text-align: center; padding: 20px; color: #686b78;">Loading orders...</p>';

    try {
        const response = await fetch('/api/admin/orders');
        const data = await response.json();

        if (!data.success || data.orders.length === 0) {
            container.innerHTML = '<p style="text-align: center; padding: 20px; color: #686b78;">No orders found.</p>';
            return;
        }

        container.innerHTML = data.orders.map(order => {
            const orderDate = new Date(order.created_at).toLocaleString();
            return `
                <div class="manage-order-card">
                    <div class="manage-order-header">
                        <div>
                            <strong>Order #${order.id}</strong> by <strong>${order.username}</strong>
                            <span style="color: #686b78; font-size: 13px; margin-left: 10px;">${orderDate}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-weight: 600;">₹${parseFloat(order.total_amount).toFixed(2)}</span>
                            <select class="status-select" onchange="updateOrderStatus(${order.id}, this.value)">
                                <option value="pending" ${order.status === 'pending' ? 'selected' : ''}>Pending</option>
                                <option value="confirmed" ${order.status === 'confirmed' ? 'selected' : ''}>Confirmed</option>
                                <option value="delivered" ${order.status === 'delivered' ? 'selected' : ''}>Delivered</option>
                                <option value="cancelled" ${order.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                            </select>
                        </div>
                    </div>
                    <div class="manage-order-details">
                        <p style="color: #686b78; font-size: 13px;">📍 ${order.address}</p>
                        <div style="margin-top: 8px;">
                            ${order.items.map(item => `
                                <span class="order-item-tag">${item.name} ×${item.quantity}</span>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        }).join('');

    } catch (error) {
        container.innerHTML = '<p style="text-align: center; padding: 20px; color: #dc3545;">Error loading orders.</p>';
        console.error(error);
    }
}

async function updateOrderStatus(orderId, newStatus) {
    const messageDiv = document.getElementById('adminMessage');
    try {
        const response = await fetch(`/api/admin/orders/${orderId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        const data = await response.json();

        if (data.success) {
            messageDiv.textContent = '✅ ' + data.message;
            messageDiv.className = 'message success';
        } else {
            messageDiv.textContent = '❌ ' + (data.message || 'Failed to update status');
            messageDiv.className = 'message error';
            loadAllOrders(); // reload to revert dropdown
        }
    } catch (error) {
        messageDiv.textContent = '❌ Error: ' + error.message;
        messageDiv.className = 'message error';
    }
}
