"""
=============================================================================
FOREVERR - DATABASE CONFIGURATION & MODELS
=============================================================================
This file initializes Flask-SQLAlchemy and defines all database models (tables)
for the Foreverr e-commerce application.

Each Python class represents a table in the MySQL 'foreverr' database:
1. User          -> users
2. Category      -> categories
3. Product       -> products
4. Cart          -> cart
5. CartItem      -> cart_items
6. Order         -> orders
7. OrderItem     -> order_items
8. Payment       -> payments
9. Review        -> reviews
10. Wishlist     -> wishlist
11. OrderTracking -> order_tracking
=============================================================================
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy object (binds with app in app.py)
db = SQLAlchemy()

# ---------------------------------------------------------------------------
# 1. USER MODEL (users table)
# Stores buyers, sellers, and administrators
# ---------------------------------------------------------------------------
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)  # Stored as secure hash
    role = db.Column(db.String(20), nullable=False, default='buyer')  # 'buyer', 'seller', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    products = db.relationship('Product', backref='seller', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='buyer', lazy=True)
    reviews = db.relationship('Review', backref='buyer', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='buyer', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


# ---------------------------------------------------------------------------
# 2. CATEGORY MODEL (categories table)
# ---------------------------------------------------------------------------
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # Relationship to products in this category
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


# ---------------------------------------------------------------------------
# 3. PRODUCT MODEL (products table)
# ---------------------------------------------------------------------------
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)               # Current selling price
    original_price = db.Column(db.Float, nullable=True)      # Original MRP before discount
    discount = db.Column(db.Integer, default=0)              # Percentage discount (e.g. 15 for 15%)
    stock = db.Column(db.Integer, default=10)                # Available inventory quantity
    image = db.Column(db.String(500), nullable=True)         # Image URL or static file path
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    cart_items = db.relationship('CartItem', backref='product', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    wishlist_entries = db.relationship('Wishlist', backref='product', lazy=True, cascade='all, delete-orphan')

    @property
    def average_rating(self):
        """Calculates average rating out of 5 stars based on customer reviews."""
        if not self.reviews:
            return 0.0
        total = sum(r.rating for r in self.reviews)
        return round(total / len(self.reviews), 1)

    @property
    def review_count(self):
        """Returns total number of approved reviews."""
        return len(self.reviews)

    def __repr__(self):
        return f'<Product {self.name} - ₹{self.price}>'


# ---------------------------------------------------------------------------
# 4. CART MODEL (cart table)
# Each user has an active shopping cart
# ---------------------------------------------------------------------------
class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to individual items inside this cart
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Cart id={self.id} user_id={self.user_id}>'


# ---------------------------------------------------------------------------
# 5. CART ITEMS MODEL (cart_items table)
# ---------------------------------------------------------------------------
class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    @property
    def item_total(self):
        """Item subtotal = unit price * quantity"""
        return round(self.product.price * self.quantity, 2)

    def __repr__(self):
        return f'<CartItem product_id={self.product_id} qty={self.quantity}>'


# ---------------------------------------------------------------------------
# 6. ORDER MODEL (orders table)
# ---------------------------------------------------------------------------
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)        # Subtotal sum of items
    discount_amount = db.Column(db.Float, default=0.0)       # Applied savings
    shipping_amount = db.Column(db.Float, default=0.0)       # Shipping charges (0 if free threshold)
    final_amount = db.Column(db.Float, nullable=False)       # Total amount payable
    status = db.Column(db.String(30), default='Placed')      # 'Placed', 'Confirmed', 'Processing', 'Shipped', 'Delivered', 'Cancelled'

    # Payment details associated directly with the order
    payment_method = db.Column(db.String(30), default='COD') # 'COD', 'UPI', 'CARD', 'NET_BANKING'
    payment_status = db.Column(db.String(30), default='Pending') # 'Pending', 'Success', 'Failed'
    transaction_id = db.Column(db.String(60), default='N/A')

    # Shipping delivery fields
    delivery_name = db.Column(db.String(100), nullable=True)
    delivery_email = db.Column(db.String(120), nullable=True)
    delivery_phone = db.Column(db.String(20), nullable=True)
    delivery_address = db.Column(db.Text, nullable=True)
    delivery_city = db.Column(db.String(60), nullable=True)
    delivery_state = db.Column(db.String(60), nullable=True)
    delivery_pincode = db.Column(db.String(20), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payment_record = db.relationship('Payment', backref='order', uselist=False, lazy=True, cascade='all, delete-orphan')
    tracking_history = db.relationship('OrderTracking', backref='order', lazy=True, cascade='all, delete-orphan', order_by='OrderTracking.updated_at')

    def __repr__(self):
        return f'<Order #{self.id} status={self.status} total=₹{self.final_amount}>'


# ---------------------------------------------------------------------------
# 7. ORDER ITEM MODEL (order_items table)
# Line items belonging to an order
# ---------------------------------------------------------------------------
class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='SET NULL'), nullable=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)               # Price at time of purchase

    @property
    def item_total(self):
        return round(self.price * self.quantity, 2)

    def __repr__(self):
        return f'<OrderItem order_id={self.order_id} prod={self.product_id} qty={self.quantity}>'


# ---------------------------------------------------------------------------
# 8. PAYMENT MODEL (payments table)
# Stores simulated payment transaction details
# ---------------------------------------------------------------------------
class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False) # 'COD', 'UPI', 'CARD', 'NET_BANKING'
    payment_status = db.Column(db.String(30), nullable=False) # 'Pending', 'Success', 'Failed'
    transaction_id = db.Column(db.String(60), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Payment {self.payment_id} method={self.payment_method} status={self.payment_status}>'


# ---------------------------------------------------------------------------
# 9. REVIEWS MODEL (reviews table)
# ---------------------------------------------------------------------------
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)            # 1 to 5 stars
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review prod={self.product_id} rating={self.rating}>'


# ---------------------------------------------------------------------------
# 10. WISHLIST MODEL (wishlist table)
# ---------------------------------------------------------------------------
class Wishlist(db.Model):
    __tablename__ = 'wishlist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<Wishlist buyer_id={self.buyer_id} product_id={self.product_id}>'


# ---------------------------------------------------------------------------
# 11. ORDER TRACKING MODEL (order_tracking table)
# Timeline step entries for an order
# ---------------------------------------------------------------------------
class OrderTracking(db.Model):
    __tablename__ = 'order_tracking'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(50), nullable=False)         # e.g., 'Order Placed', 'Payment Confirmed'
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<OrderTracking order={self.order_id} status={self.status}>'
