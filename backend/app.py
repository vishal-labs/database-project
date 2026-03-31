from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, 
            static_folder='../frontend', 
            template_folder='../frontend', 
            static_url_path='')
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def get_db_connection():
    """Create and return database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# ============================================================================
# PAGE ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/restaurants')
def restaurants_page():
    return render_template('restaurants.html')

@app.route('/cart')
def cart_page():
    return render_template('cart.html')

@app.route('/db-test')
def db_test_page():
    return render_template('db_test.html')

@app.route('/orders')
def orders_page():
    return render_template('orders.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

# Serve static files (JS, CSS) - must be after page routes
@app.route('/<filename>')
def serve_static_files(filename):
    """Serve static files (JS, CSS) from frontend directory"""
    import os
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    # Only serve .js, .css files that actually exist
    if filename.endswith(('.js', '.css')):
        file_path = os.path.join(frontend_path, filename)
        if os.path.exists(file_path):
            return send_from_directory(frontend_path, filename)
    return "File not found", 404

# ============================================================================
# API ROUTES - AUTH
# ============================================================================

@app.route('/api/db-test', methods=['GET'])
def test_db_connection():
    """Test database connection endpoint"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database connection failed',
                'error': 'Could not establish connection. Check your .env file settings.'
            }), 500
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables] if tables else []
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Database connection successful!',
            'tables': table_names,
            'table_count': len(table_names)
        })
    except Error as e:
        return jsonify({
            'success': False,
            'message': 'Database connection failed',
            'error': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Unexpected error',
            'error': str(e)
        }), 500

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        check_query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(check_query, (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        insert_query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (username, password, email))
        conn.commit()
        
        user_id = cursor.lastrowid
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {'id': user_id, 'username': username}
        })
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        
        if user:
            # Check for admin privileges (vishal with password 'password')
            is_admin = (username.lower() == 'admin' and password == 'admin123')
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user['id'], 
                    'username': user['username'],
                    'is_admin': is_admin
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

# ============================================================================
# API ROUTES - USER PROFILE
# ============================================================================

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User ID required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # Get order count
        cursor.execute("SELECT COUNT(*) as order_count FROM orders WHERE user_id = %s", (user_id,))
        stats = cursor.fetchone()

        return jsonify({
            'success': True,
            'profile': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'] or '',
                'created_at': str(user['created_at']),
                'order_count': stats['order_count']
            }
        })
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    """Update user profile (email)"""
    data = request.json
    user_id = data.get('user_id')
    email = data.get('email', '')

    if not user_id:
        return jsonify({'success': False, 'message': 'User ID required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("UPDATE users SET email = %s WHERE id = %s", (email, user_id))
        conn.commit()

        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

# ============================================================================
# API ROUTES - RESTAURANTS & ITEMS
# ============================================================================

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    """Get all restaurants"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM restaurants"
        cursor.execute(query)
        restaurants = cursor.fetchall()
        return jsonify({'success': True, 'restaurants': restaurants})
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/restaurants/<int:restaurant_id>/items', methods=['GET'])
def get_restaurant_items(restaurant_id):
    """Get items for a specific restaurant"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM items WHERE restaurant_id = %s"
        cursor.execute(query, (restaurant_id,))
        items = cursor.fetchall()
        return jsonify({'success': True, 'items': items})
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/search', methods=['GET'])
def search_items():
    """Search menu items by name across all restaurants"""
    query_str = request.args.get('q', '').strip()
    if not query_str:
        return jsonify({'success': True, 'items': []})

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        search_query = """
            SELECT i.*, r.name as restaurant_name 
            FROM items i 
            JOIN restaurants r ON i.restaurant_id = r.id 
            WHERE i.name LIKE %s OR i.description LIKE %s
            ORDER BY i.name
        """
        search_term = f"%{query_str}%"
        cursor.execute(search_query, (search_term, search_term))
        items = cursor.fetchall()
        return jsonify({'success': True, 'items': items})
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

# ============================================================================
# API ROUTES - CART (User-specific)
# ============================================================================

@app.route('/api/cart', methods=['GET', 'POST', 'PUT', 'DELETE'])
def cart():
    """Cart operations - user-specific"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'GET':
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'message': 'User ID required'}), 400

            query = """
                SELECT c.*, i.name, i.price, i.description, r.name as restaurant_name 
                FROM cart c 
                JOIN items i ON c.item_id = i.id 
                JOIN restaurants r ON i.restaurant_id = r.id
                WHERE c.user_id = %s
            """
            cursor.execute(query, (user_id,))
            cart_items = cursor.fetchall()
            return jsonify({'success': True, 'cart': cart_items})
        
        elif request.method == 'POST':
            data = request.json
            item_id = data.get('item_id')
            quantity = data.get('quantity', 1)
            user_id = data.get('user_id')
            
            if not item_id:
                return jsonify({'success': False, 'message': 'Item ID required'}), 400
            if not user_id:
                return jsonify({'success': False, 'message': 'User ID required'}), 400
            
            # Check if item already in cart for this user
            check_query = "SELECT * FROM cart WHERE item_id = %s AND user_id = %s"
            cursor.execute(check_query, (item_id, user_id))
            existing = cursor.fetchone()
            
            if existing:
                update_query = "UPDATE cart SET quantity = quantity + %s WHERE item_id = %s AND user_id = %s"
                cursor.execute(update_query, (quantity, item_id, user_id))
            else:
                insert_query = "INSERT INTO cart (user_id, item_id, quantity) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (user_id, item_id, quantity))
            
            conn.commit()
            return jsonify({'success': True, 'message': 'Item added to cart'})

        elif request.method == 'PUT':
            # Update quantity
            data = request.json
            item_id = data.get('item_id')
            quantity = data.get('quantity')
            user_id = data.get('user_id')

            if not item_id or quantity is None or not user_id:
                return jsonify({'success': False, 'message': 'Item ID, quantity, and user ID required'}), 400

            if quantity <= 0:
                # Remove item if quantity is 0 or less
                delete_query = "DELETE FROM cart WHERE item_id = %s AND user_id = %s"
                cursor.execute(delete_query, (item_id, user_id))
            else:
                update_query = "UPDATE cart SET quantity = %s WHERE item_id = %s AND user_id = %s"
                cursor.execute(update_query, (quantity, item_id, user_id))

            conn.commit()
            return jsonify({'success': True, 'message': 'Cart updated'})
        
        elif request.method == 'DELETE':
            data = request.json
            item_id = data.get('item_id')
            user_id = data.get('user_id')
            
            if not item_id:
                return jsonify({'success': False, 'message': 'Item ID required'}), 400
            if not user_id:
                return jsonify({'success': False, 'message': 'User ID required'}), 400
            
            delete_query = "DELETE FROM cart WHERE item_id = %s AND user_id = %s"
            cursor.execute(delete_query, (item_id, user_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Item removed from cart'})
    
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

# ============================================================================
# API ROUTES - CHECKOUT & ORDERS
# ============================================================================

@app.route('/api/checkout', methods=['POST'])
def checkout():
    """Process checkout"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        data = request.json
        address = data.get('address')
        user_id = data.get('user_id')
        
        if not address:
            return jsonify({'success': False, 'message': 'Address required'}), 400
        if not user_id:
            return jsonify({'success': False, 'message': 'User must be logged in to place order'}), 401
        
        cursor = conn.cursor(dictionary=True)
        
        # Get cart items for this user
        cart_query = "SELECT * FROM cart WHERE user_id = %s"
        cursor.execute(cart_query, (user_id,))
        cart_items = cursor.fetchall()
        
        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'}), 400
        
        # Calculate total
        total = 0
        for item in cart_items:
            item_query = "SELECT price FROM items WHERE id = %s"
            cursor.execute(item_query, (item['item_id'],))
            item_data = cursor.fetchone()
            total += item_data['price'] * item['quantity']
        
        # Create order
        order_query = "INSERT INTO orders (user_id, address, total_amount, status) VALUES (%s, %s, %s, %s)"
        cursor.execute(order_query, (user_id, address, total, 'pending'))
        order_id = cursor.lastrowid
        
        # Create order items
        for item in cart_items:
            item_query = "SELECT price FROM items WHERE id = %s"
            cursor.execute(item_query, (item['item_id'],))
            item_data = cursor.fetchone()
            order_item_query = "INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (%s, %s, %s, %s)"
            cursor.execute(order_item_query, (order_id, item['item_id'], item['quantity'], item_data['price']))
        
        # Clear cart for this user
        clear_cart_query = "DELETE FROM cart WHERE user_id = %s"
        cursor.execute(clear_cart_query, (user_id,))
        
        conn.commit()
        return jsonify({'success': True, 'message': 'Order placed successfully', 'order_id': order_id})
    
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/orders', methods=['GET'])
def get_user_orders():
    """Get order history for logged in user"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'User ID required'}), 400
        
        cursor = conn.cursor(dictionary=True)
        
        orders_query = """
            SELECT o.*, 
                   COUNT(oi.id) as item_count
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE o.user_id = %s
            GROUP BY o.id
            ORDER BY o.created_at DESC
        """
        cursor.execute(orders_query, (user_id,))
        orders = cursor.fetchall()
        
        for order in orders:
            items_query = """
                SELECT oi.*, i.name, i.description, r.name as restaurant_name
                FROM order_items oi
                JOIN items i ON oi.item_id = i.id
                JOIN restaurants r ON i.restaurant_id = r.id
                WHERE oi.order_id = %s
            """
            cursor.execute(items_query, (order['id'],))
            order['items'] = cursor.fetchall()
        
        return jsonify({'success': True, 'orders': orders})
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/orders/<int:order_id>/cancel', methods=['PUT'])
def cancel_order(order_id):
    """Cancel an order (only if pending)"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        data = request.json
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'User ID required'}), 400

        cursor = conn.cursor(dictionary=True)

        # Verify order belongs to user and is pending
        cursor.execute("SELECT * FROM orders WHERE id = %s AND user_id = %s", (order_id, user_id))
        order = cursor.fetchone()

        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404

        if order['status'] != 'pending':
            return jsonify({'success': False, 'message': 'Only pending orders can be cancelled'}), 400

        cursor.execute("UPDATE orders SET status = 'cancelled' WHERE id = %s", (order_id,))
        conn.commit()

        return jsonify({'success': True, 'message': 'Order cancelled successfully'})
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

# ============================================================================
# API ROUTES - ADMIN
# ============================================================================

@app.route('/api/admin/add-restaurant', methods=['POST'])
def add_restaurant():
    """Admin endpoint to add a new restaurant"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'success': False, 'message': 'Restaurant name required'}), 400
        
        cursor = conn.cursor(dictionary=True)
        insert_query = "INSERT INTO restaurants (name, description) VALUES (%s, %s)"
        cursor.execute(insert_query, (name, description))
        conn.commit()
        
        restaurant_id = cursor.lastrowid
        return jsonify({
            'success': True,
            'message': 'Restaurant added successfully',
            'restaurant': {'id': restaurant_id, 'name': name, 'description': description}
        })
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/admin/add-item', methods=['POST'])
def add_item():
    """Admin endpoint to add a new menu item"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    try:
        data = request.json
        restaurant_id = data.get('restaurant_id')
        name = data.get('name')
        description = data.get('description', '')
        price = data.get('price')
        
        if not restaurant_id or not name or not price:
            return jsonify({'success': False, 'message': 'Restaurant ID, name, and price are required'}), 400
        
        cursor = conn.cursor(dictionary=True)
        check_query = "SELECT * FROM restaurants WHERE id = %s"
        cursor.execute(check_query, (restaurant_id,))
        restaurant = cursor.fetchone()
        
        if not restaurant:
            return jsonify({'success': False, 'message': 'Restaurant not found'}), 404
        
        insert_query = "INSERT INTO items (restaurant_id, name, description, price) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (restaurant_id, name, description, price))
        conn.commit()
        
        item_id = cursor.lastrowid
        return jsonify({
            'success': True,
            'message': 'Item added successfully',
            'item': {'id': item_id, 'restaurant_id': restaurant_id, 'name': name, 'description': description, 'price': price}
        })
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/admin/delete-restaurant/<int:restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    """Admin endpoint to delete a restaurant"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        # Check restaurant exists
        cursor.execute("SELECT * FROM restaurants WHERE id = %s", (restaurant_id,))
        restaurant = cursor.fetchone()
        if not restaurant:
            return jsonify({'success': False, 'message': 'Restaurant not found'}), 404

        # Delete (cascade will remove items, cart entries)
        cursor.execute("DELETE FROM restaurants WHERE id = %s", (restaurant_id,))
        conn.commit()

        return jsonify({'success': True, 'message': f'Restaurant "{restaurant["name"]}" deleted successfully'})
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/admin/rename-restaurant/<int:restaurant_id>', methods=['PUT'])
def rename_restaurant(restaurant_id):
    """Admin endpoint to rename a restaurant"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        data = request.json
        new_name = data.get('name', '').strip()

        if not new_name:
            return jsonify({'success': False, 'message': 'Restaurant name is required'}), 400

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM restaurants WHERE id = %s", (restaurant_id,))
        restaurant = cursor.fetchone()
        if not restaurant:
            return jsonify({'success': False, 'message': 'Restaurant not found'}), 404

        cursor.execute("UPDATE restaurants SET name = %s WHERE id = %s", (new_name, restaurant_id))
        conn.commit()

        return jsonify({'success': True, 'message': f'Restaurant renamed to "{new_name}"'})
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/admin/delete-item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Admin endpoint to delete a menu item"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404

        cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
        conn.commit()

        return jsonify({'success': True, 'message': f'Item "{item["name"]}" deleted successfully'})
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/admin/orders', methods=['GET'])
def get_all_orders():
    """Admin endpoint to get all orders"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        orders_query = """
            SELECT o.*, u.username,
                   COUNT(oi.id) as item_count
            FROM orders o
            JOIN users u ON o.user_id = u.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            GROUP BY o.id
            ORDER BY o.created_at DESC
        """
        cursor.execute(orders_query)
        orders = cursor.fetchall()

        for order in orders:
            items_query = """
                SELECT oi.*, i.name, r.name as restaurant_name
                FROM order_items oi
                JOIN items i ON oi.item_id = i.id
                JOIN restaurants r ON i.restaurant_id = r.id
                WHERE oi.order_id = %s
            """
            cursor.execute(items_query, (order['id'],))
            order['items'] = cursor.fetchall()

        return jsonify({'success': True, 'orders': orders})
    except Error as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Admin endpoint to update order status"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        data = request.json
        new_status = data.get('status')

        valid_statuses = ['pending', 'confirmed', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404

        cursor.execute("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))
        conn.commit()

        return jsonify({'success': True, 'message': f'Order #{order_id} status updated to {new_status}'})
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
