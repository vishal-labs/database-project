# Viggy - Simple Food Ordering Application

A lightweight food ordering application built with Flask backend and vanilla JavaScript frontend.

## Features

- User login (no password hashing)
- 3 restaurants with at least 3 items each
- Add to cart functionality
- Checkout with address input

## Project Structure

```
DBMS_project/
├── backend/
│   └── app.py              # Flask backend application
├── frontend/
│   ├── index.html          # Home page
│   ├── login.html          # Login page
│   ├── restaurants.html    # Restaurant listing page
│   ├── cart.html           # Shopping cart page
│   ├── styles.css          # Stylesheet
│   ├── login.js            # Login functionality
│   ├── restaurants.js      # Restaurant and menu display
│   └── cart.js             # Cart management
├── sql/
│   ├── create_tables.sql   # Database schema
│   └── insert_data.sql     # Sample data
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
├── FEATURES.md             # Detailed features documentation
└── CHANGELOG.md            # Project changelog
```

## Setup Instructions

### 1. Database Configuration

Copy `.env.example` to `.env` and fill in your database details:

```bash
cp .env.example .env
```

Edit `.env` with your MySQL database credentials:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=swiggy_clone
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Once your database is connected, run the SQL scripts:

```bash
# Create tables
mysql -u your_username -p your_database < sql/create_tables.sql

# Insert sample data
mysql -u your_username -p your_database < sql/insert_data.sql
```

Or execute them directly in your MySQL client.

### 4. Run the Application

```bash
cd backend
python app.py
```

The application will run on `http://localhost:5000`

## Usage

1. **Login**: Use one of the sample users:
   - Username: `user1`, Password: `password1`
   - Username: `user2`, Password: `password2`
   - Username: `admin`, Password: `admin123`

2. **Browse Restaurants**: View available restaurants and their menu items

3. **Add to Cart**: Click "Add to Cart" on any item

4. **Checkout**: Go to cart, enter delivery address, and place order

## API Endpoints

- `POST /api/login` - User login
- `GET /api/restaurants` - Get all restaurants
- `GET /api/restaurants/<id>/items` - Get items for a restaurant
- `GET /api/cart` - Get cart items
- `POST /api/cart` - Add item to cart
- `DELETE /api/cart` - Remove item from cart
- `POST /api/checkout` - Place order

## Database Schema

- **users**: User accounts
- **restaurants**: Restaurant information
- **items**: Menu items
- **cart**: Shopping cart
- **orders**: Order records
- **order_items**: Order line items

## Notes

- Passwords are stored in plain text (no hashing) as per requirements
- Simple, lightweight design - no heavy frameworks
- Cart is session-based (not user-specific in current implementation)

## Documentation

- See `FEATURES.md` for detailed feature documentation
- See `CHANGELOG.md` for version history

