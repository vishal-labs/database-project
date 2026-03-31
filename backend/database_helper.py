"""
Database Helper File
Contains all table schemas, column information, and database structure reference.
Use this file to understand the database schema and table relationships.
"""

# ============================================================================
# DATABASE SCHEMA REFERENCE
# ============================================================================

TABLES = {
    'users': {
        'name': 'users',
        'description': 'Stores user account information',
        'columns': {
            'id': {
                'type': 'INT',
                'constraints': 'AUTO_INCREMENT PRIMARY KEY',
                'description': 'Unique user identifier'
            },
            'username': {
                'type': 'VARCHAR(50)',
                'constraints': 'NOT NULL UNIQUE',
                'description': 'Unique username for login'
            },
            'password': {
                'type': 'VARCHAR(255)',
                'constraints': 'NOT NULL',
                'description': 'User password (plain text, no hashing)'
            },
            'email': {
                'type': 'VARCHAR(100)',
                'constraints': 'NULL',
                'description': 'User email address (optional)'
            },
            'created_at': {
                'type': 'TIMESTAMP',
                'constraints': 'DEFAULT CURRENT_TIMESTAMP',
                'description': 'Account creation timestamp'
            }
        },
        'relationships': {
            'referenced_by': ['orders'],
            'description': 'Users can have multiple orders'
        }
    },
    
    'restaurants': {
        'name': 'restaurants',
        'description': 'Stores restaurant information',
        'columns': {
            'id': {
                'type': 'INT',
                'constraints': 'AUTO_INCREMENT PRIMARY KEY',
                'description': 'Unique restaurant identifier'
            },
            'name': {
                'type': 'VARCHAR(100)',
                'constraints': 'NOT NULL',
                'description': 'Restaurant name'
            },
            'description': {
                'type': 'TEXT',
                'constraints': 'NULL',
                'description': 'Restaurant description'
            },
            'created_at': {
                'type': 'TIMESTAMP',
                'constraints': 'DEFAULT CURRENT_TIMESTAMP',
                'description': 'Restaurant creation timestamp'
            }
        },
        'relationships': {
            'references': [],
            'referenced_by': ['items'],
            'description': 'Restaurants have multiple menu items'
        }
    },
    
    'items': {
        'name': 'items',
        'description': 'Stores menu items for restaurants',
        'columns': {
            'id': {
                'type': 'INT',
                'constraints': 'AUTO_INCREMENT PRIMARY KEY',
                'description': 'Unique item identifier'
            },
            'restaurant_id': {
                'type': 'INT',
                'constraints': 'NOT NULL',
                'description': 'Foreign key to restaurants table',
                'foreign_key': 'restaurants(id) ON DELETE CASCADE'
            },
            'name': {
                'type': 'VARCHAR(100)',
                'constraints': 'NOT NULL',
                'description': 'Item name'
            },
            'description': {
                'type': 'TEXT',
                'constraints': 'NULL',
                'description': 'Item description'
            },
            'price': {
                'type': 'DECIMAL(10, 2)',
                'constraints': 'NOT NULL',
                'description': 'Item price in rupees'
            },
            'created_at': {
                'type': 'TIMESTAMP',
                'constraints': 'DEFAULT CURRENT_TIMESTAMP',
                'description': 'Item creation timestamp'
            }
        },
        'relationships': {
            'references': ['restaurants'],
            'referenced_by': ['cart', 'order_items'],
            'description': 'Items belong to restaurants and can be in cart/orders'
        }
    },
    
    'cart': {
        'name': 'cart',
        'description': 'Stores items in shopping cart (user-specific)',
        'columns': {
            'id': {
                'type': 'INT',
                'constraints': 'AUTO_INCREMENT PRIMARY KEY',
                'description': 'Unique cart entry identifier'
            },
            'user_id': {
                'type': 'INT',
                'constraints': 'NOT NULL',
                'description': 'Foreign key to users table',
                'foreign_key': 'users(id) ON DELETE CASCADE'
            },
            'item_id': {
                'type': 'INT',
                'constraints': 'NOT NULL',
                'description': 'Foreign key to items table',
                'foreign_key': 'items(id) ON DELETE CASCADE'
            },
            'quantity': {
                'type': 'INT',
                'constraints': 'NOT NULL DEFAULT 1',
                'description': 'Quantity of item in cart'
            },
            'created_at': {
                'type': 'TIMESTAMP',
                'constraints': 'DEFAULT CURRENT_TIMESTAMP',
                'description': 'Cart entry creation timestamp'
            }
        },
        'relationships': {
            'references': ['users', 'items'],
            'referenced_by': [],
            'description': 'Cart contains items, scoped to individual users'
        }
    },
    
    'orders': {
        'name': 'orders',
        'description': 'Stores order information',
        'columns': {
            'id': {
                'type': 'INT',
                'constraints': 'AUTO_INCREMENT PRIMARY KEY',
                'description': 'Unique order identifier'
            },
            'user_id': {
                'type': 'INT',
                'constraints': 'NOT NULL',
                'description': 'Foreign key to users table',
                'foreign_key': 'users(id)'
            },
            'address': {
                'type': 'TEXT',
                'constraints': 'NOT NULL',
                'description': 'Delivery address'
            },
            'total_amount': {
                'type': 'DECIMAL(10, 2)',
                'constraints': 'NOT NULL',
                'description': 'Total order amount in rupees'
            },
            'status': {
                'type': 'VARCHAR(50)',
                'constraints': 'DEFAULT "pending"',
                'description': 'Order status (pending, confirmed, delivered, etc.)'
            },
            'created_at': {
                'type': 'TIMESTAMP',
                'constraints': 'DEFAULT CURRENT_TIMESTAMP',
                'description': 'Order creation timestamp'
            }
        },
        'relationships': {
            'references': ['users'],
            'referenced_by': ['order_items'],
            'description': 'Orders belong to users and contain multiple order items'
        }
    },
    
    'order_items': {
        'name': 'order_items',
        'description': 'Stores individual items in each order',
        'columns': {
            'id': {
                'type': 'INT',
                'constraints': 'AUTO_INCREMENT PRIMARY KEY',
                'description': 'Unique order item identifier'
            },
            'order_id': {
                'type': 'INT',
                'constraints': 'NOT NULL',
                'description': 'Foreign key to orders table',
                'foreign_key': 'orders(id) ON DELETE CASCADE'
            },
            'item_id': {
                'type': 'INT',
                'constraints': 'NOT NULL',
                'description': 'Foreign key to items table',
                'foreign_key': 'items(id)'
            },
            'quantity': {
                'type': 'INT',
                'constraints': 'NOT NULL',
                'description': 'Quantity of item ordered'
            },
            'price': {
                'type': 'DECIMAL(10, 2)',
                'constraints': 'NOT NULL',
                'description': 'Price of item at time of order'
            },
            'created_at': {
                'type': 'TIMESTAMP',
                'constraints': 'DEFAULT CURRENT_TIMESTAMP',
                'description': 'Order item creation timestamp'
            }
        },
        'relationships': {
            'references': ['orders', 'items'],
            'referenced_by': [],
            'description': 'Order items link orders to specific items with quantities'
        }
    }
}

# ============================================================================
# TABLE CREATION ORDER
# ============================================================================
# Tables must be created in this order due to foreign key dependencies:
CREATION_ORDER = [
    'users',        # No dependencies
    'restaurants',  # No dependencies
    'items',        # Depends on restaurants
    'cart',         # Depends on items
    'orders',       # Depends on users
    'order_items'   # Depends on orders and items
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_table_schema(table_name):
    """Get schema information for a specific table"""
    return TABLES.get(table_name, None)

def get_all_tables():
    """Get list of all table names"""
    return list(TABLES.keys())

def get_table_columns(table_name):
    """Get column information for a specific table"""
    table = TABLES.get(table_name)
    if table:
        return table['columns']
    return None

def get_foreign_keys(table_name):
    """Get foreign key relationships for a specific table"""
    table = TABLES.get(table_name)
    if table:
        return table.get('relationships', {})
    return None

# ============================================================================
# SAMPLE DATA STRUCTURE
# ============================================================================

SAMPLE_DATA = {
    'users': [
        {'username': 'user1', 'password': 'password1', 'email': 'user1@example.com'},
        {'username': 'user2', 'password': 'password2', 'email': 'user2@example.com'},
        {'username': 'admin', 'password': 'admin123', 'email': 'admin@example.com'}
    ],
    'restaurants': [
        {'name': 'Pizza Palace', 'description': 'Delicious pizzas and Italian cuisine'},
        {'name': 'Burger King', 'description': 'Juicy burgers and fast food'},
        {'name': 'Sushi Express', 'description': 'Fresh sushi and Japanese dishes'}
    ],
    'items': [
        # Pizza Palace items (restaurant_id = 1)
        {'restaurant_id': 1, 'name': 'Margherita Pizza', 'description': 'Classic pizza with tomato and mozzarella', 'price': 299.00},
        {'restaurant_id': 1, 'name': 'Pepperoni Pizza', 'description': 'Pizza with pepperoni and cheese', 'price': 399.00},
        {'restaurant_id': 1, 'name': 'Veggie Supreme', 'description': 'Pizza loaded with vegetables', 'price': 349.00},
        # Burger King items (restaurant_id = 2)
        {'restaurant_id': 2, 'name': 'Classic Burger', 'description': 'Beef patty with lettuce and tomato', 'price': 199.00},
        {'restaurant_id': 2, 'name': 'Chicken Burger', 'description': 'Grilled chicken burger with special sauce', 'price': 249.00},
        {'restaurant_id': 2, 'name': 'Veg Burger', 'description': 'Vegetarian burger with fresh veggies', 'price': 179.00},
        # Sushi Express items (restaurant_id = 3)
        {'restaurant_id': 3, 'name': 'Salmon Sushi', 'description': 'Fresh salmon sushi rolls', 'price': 449.00},
        {'restaurant_id': 3, 'name': 'California Roll', 'description': 'Crab and avocado roll', 'price': 299.00},
        {'restaurant_id': 3, 'name': 'Dragon Roll', 'description': 'Eel and cucumber roll', 'price': 399.00}
    ]
}

