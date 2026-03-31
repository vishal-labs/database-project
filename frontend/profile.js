// Profile page logic
document.addEventListener('DOMContentLoaded', function() {
    const user = loadUserInfo();
    if (!user) {
        alert('Please login to view your profile');
        window.location.href = '/login';
        return;
    }
    
    loadProfile(user.id);
});

async function loadProfile(userId) {
    try {
        const response = await fetch(`/api/profile?user_id=${userId}`);
        const data = await response.json();
        
        if (data.success) {
            const profile = data.profile;
            document.getElementById('profileUsername').textContent = profile.username;
            document.getElementById('profileEmail').value = profile.email || '';
            document.getElementById('profileOrderCount').textContent = profile.order_count;
            
            const createdDate = new Date(profile.created_at).toLocaleDateString('en-IN', {
                year: 'numeric', month: 'long', day: 'numeric'
            });
            document.getElementById('profileMemberSince').textContent = `Member since ${createdDate}`;
        } else {
            showProfileMessage('❌ Error loading profile: ' + (data.message || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error loading profile:', error);
        showProfileMessage('❌ Error: ' + error.message, 'error');
    }
}

document.getElementById('editProfileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const user = loadUserInfo();
    if (!user) return;
    
    const email = document.getElementById('profileEmail').value.trim();
    const submitBtn = document.querySelector('#editProfileForm button[type="submit"]');
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Updating...';
    
    try {
        const response = await fetch('/api/profile', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: user.id, email })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showProfileMessage('✅ Profile updated successfully!', 'success');
        } else {
            showProfileMessage('❌ ' + (data.message || 'Failed to update profile'), 'error');
        }
    } catch (error) {
        showProfileMessage('❌ Error: ' + error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Update Profile';
    }
});

function showProfileMessage(text, type) {
    const messageDiv = document.getElementById('profileMessage');
    messageDiv.textContent = text;
    messageDiv.className = 'message ' + type;
    setTimeout(() => {
        messageDiv.textContent = '';
        messageDiv.className = 'message';
    }, 4000);
}
