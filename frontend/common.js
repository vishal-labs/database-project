// Common functions for all pages

function loadUserInfo() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        try {
            return JSON.parse(userStr);
        } catch (e) {
            return null;
        }
    }
    return null;
}

function updateHeader() {
    const user = loadUserInfo();
    const nav = document.querySelector('nav');
    
    if (nav) {
        // Clear existing user info
        const existingUserInfo = nav.querySelector('.user-info');
        if (existingUserInfo) {
            existingUserInfo.remove();
        }
        
        // Hide/show login/register links based on login status
        const loginLink = nav.querySelector('a[href="/login"]');
        const registerLink = nav.querySelector('a[href="/register"]');
        
        if (user) {
            // Hide login/register links
            if (loginLink) loginLink.style.display = 'none';
            if (registerLink) registerLink.style.display = 'none';
            
            // Create user info section
            const userInfo = document.createElement('div');
            userInfo.className = 'user-info';
            userInfo.innerHTML = `
                <span class="username">👤 ${user.username}</span>
                <a href="/profile" class="orders-link">Profile</a>
                <a href="/orders" class="orders-link">Orders</a>
                ${user.is_admin ? '<a href="/admin" class="admin-link">Admin Panel</a>' : ''}
                <button onclick="logout()" class="logout-btn">Logout</button>
            `;
            nav.appendChild(userInfo);
        } else {
            // Show login/register links
            if (loginLink) loginLink.style.display = '';
            if (registerLink) registerLink.style.display = '';
            
            // Add links if they don't exist
            if (!loginLink) {
                const login = document.createElement('a');
                login.href = '/login';
                login.textContent = 'Login';
                nav.appendChild(login);
            }
            if (!registerLink) {
                const register = document.createElement('a');
                register.href = '/register';
                register.textContent = 'Register';
                nav.appendChild(register);
            }
        }
    }
}

function logout() {
    localStorage.removeItem('user');
    window.location.href = '/';
}

function checkLogin(redirectTo = '/login') {
    const user = loadUserInfo();
    if (!user) {
        window.location.href = redirectTo;
        return false;
    }
    return true;
}

// Update header on page load
document.addEventListener('DOMContentLoaded', function() {
    updateHeader();
});

