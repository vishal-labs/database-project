# Features Documentation

## Overview
This is a simple food ordering application (Viggy) with food ordering functionality for users and management tools for admins.

## Implemented Features

### 1. User Authentication
- **Login System**: Simple username/password login (no password hashing for simplicity)
- **Registration**: New users can register with username, password, and optional email
- **User Management**: Users can log in and access the application
- **Session**: User information stored in localStorage after login

### 2. User Profile
- **View Profile**: Users can view their username, email, member-since date, and total order count
- **Edit Email**: Users can update their email address from the profile page

### 3. Restaurant Management
- **Restaurant Listing**: Display all available restaurants
- **Restaurant Details**: Each restaurant shows name and description
- **Search**: Search for dishes by name across all restaurants with real-time results

### 4. Menu Items
- **Item Display**: Each restaurant displays its menu items
- **Item Information**: Shows name, description, and price
- **Minimum Items**: Each restaurant has at least 3 items

### 5. Shopping Cart (User-Specific)
- **Add to Cart**: Users can add items to cart (requires login)
- **Cart Display**: View all items in cart with details
- **Quantity Controls**: +/- buttons to adjust item quantity
- **Remove Items**: Remove individual items from cart
- **User-Specific**: Each user has their own cart (cart is tied to user_id)
- **Total Calculation**: Automatic total cart value calculation

### 6. Checkout Process
- **Address Input**: Single field for delivery address
- **Order Placement**: Direct checkout after entering address
- **Order Processing**: Creates order record, saves order items, clears cart, shows confirmation

### 7. Order History
- **View Orders**: Users can see all their past orders with status, items, and totals
- **Cancel Orders**: Users can cancel pending orders (only if status is "pending")
- **Status Display**: Visual status badges (pending, confirmed, delivered, cancelled)

### 8. Admin Panel
- **Add Restaurant**: Create new restaurants with name and description
- **Add Menu Item**: Add items to any restaurant with name, description, and price
- **Delete Restaurant**: Remove restaurants (cascades to items)
- **Delete Menu Item**: Remove individual menu items
- **View All Orders**: See orders from all users with details
- **Update Order Status**: Change order status (pending → confirmed → delivered → cancelled)
- **Admin Access**: Only admin users can access the panel

## Technical Features

### Backend
- Flask-based REST API
- MySQL database integration
- User-specific cart operations
- Full CRUD for restaurants, items, and orders
- Error handling and validation

### Frontend
- Lightweight HTML/CSS/JavaScript
- Responsive design with mobile support
- Search with debounce
- Real-time notifications
- No heavy frameworks or libraries

### Database
- MySQL database
- Normalized schema with foreign keys
- User-specific cart (user_id foreign key)
- Tables: users, restaurants, items, cart, orders, order_items

## API Endpoints

### Auth
- `POST /api/register` - User registration
- `POST /api/login` - User login

### Profile
- `GET /api/profile?user_id=` - Get user profile
- `PUT /api/profile` - Update user email

### Restaurants & Items
- `GET /api/restaurants` - Get all restaurants
- `GET /api/restaurants/<id>/items` - Get items for a restaurant
- `GET /api/search?q=` - Search items by name

### Cart
- `GET /api/cart?user_id=` - Get cart items
- `POST /api/cart` - Add item to cart
- `PUT /api/cart` - Update item quantity
- `DELETE /api/cart` - Remove item from cart

### Orders
- `POST /api/checkout` - Place order
- `GET /api/orders?user_id=` - Get user order history
- `PUT /api/orders/<id>/cancel` - Cancel pending order

### Admin
- `POST /api/admin/add-restaurant` - Add restaurant
- `POST /api/admin/add-item` - Add menu item
- `DELETE /api/admin/delete-restaurant/<id>` - Delete restaurant
- `DELETE /api/admin/delete-item/<id>` - Delete menu item
- `GET /api/admin/orders` - Get all orders
- `PUT /api/admin/orders/<id>/status` - Update order status
