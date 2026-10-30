"""
=============================================================================
FOREVERR – E-Commerce Web Application (Flask + MySQL)
College Mini-Project (TYCS)
=============================================================================
Architecture:
- Frontend: HTML5, CSS3, JavaScript (Vanilla, Responsive)
- Backend: Python 3, Flask, Jinja2 Templates
- Database: MySQL with Flask-SQLAlchemy ORM and PyMySQL connector
=============================================================================
"""

import os
import random
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, abort, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from database import (
    db, User, Category, Product, Cart, CartItem,
    Order, OrderItem, Payment, Review, Wishlist, OrderTracking
)

# ---------------------------------------------------------------------------
# FLASK APPLICATION INITIALIZATION
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)

# Bind SQLAlchemy to Flask application
db.init_app(app)


# ---------------------------------------------------------------------------
# AUTHENTICATION & ROLE-BASED ACCESS CONTROL (RBAC) DECORATORS
# ---------------------------------------------------------------------------
def login_required(f):
    """Restricts route access to logged-in users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def seller_required(f):
    """Restricts route access to Sellers only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'seller':
            flash('Access restricted: Seller account required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Restricts route access to Administrators only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Access restricted: Administrator privileges required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------------------------------------------------
# CONTEXT PROCESSOR (Injected into every Jinja2 template)
# ---------------------------------------------------------------------------
@app.context_processor
def inject_global_data():
    """
    Passes cart count, wishlist count, active user info and categories
    to all templates automatically without querying in every route.
    """
    cart_count = 0
    wishlist_count = 0
    current_user = None

    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
        if current_user:
            user_cart = Cart.query.filter_by(user_id=current_user.id).first()
            if user_cart:
                cart_count = sum(item.quantity for item in user_cart.items)
            wishlist_count = Wishlist.query.filter_by(buyer_id=current_user.id).count()

    all_categories = Category.query.order_by(Category.name).all()
    return dict(
        current_user=current_user,
        cart_count=cart_count,
        wishlist_count=wishlist_count,
        all_categories=all_categories,
        year=datetime.utcnow().year
    )


# ===========================================================================
# 8 CORE ALGORITHMS FOR COLLEGE DEMO & VIVA VOCE
# ===========================================================================

def algorithm_1_search_products(query_text):
    """
    ALGORITHM 1: TOKEN / KEYWORD MATCHING SEARCH ALGORITHM
    Explanation for Viva:
    1. Splits the user search string into lowercase keyword tokens (e.g. 'heart pendant' -> ['heart', 'pendant']).
    2. Builds a filter query that checks whether any token appears inside:
       - Product Name (ILIKE %token%)
       - Product Description (ILIKE %token%)
       - Category Name (joined from categories table)
    3. Returns matched products from MySQL database.
    """
    if not query_text or not query_text.strip():
        return Product.query

    tokens = [t.strip().lower() for t in query_text.split() if t.strip()]
    query = Product.query.join(Category, isouter=True)

    for token in tokens:
        search_pattern = f"%{token}%"
        query = query.filter(
            db.or_(
                Product.name.ilike(search_pattern),
                Product.description.ilike(search_pattern),
                Category.name.ilike(search_pattern)
            )
        )
    return query


def algorithm_2_sort_products(query, sort_by):
    """
    ALGORITHM 2: PRODUCT SORTING ALGORITHM
    Explanation for Viva:
    Applies ORDER BY clauses depending on user selection:
    - 'newest': Created date descending
    - 'oldest': Created date ascending
    - 'price_asc': Selling price low to high
    - 'price_desc': Selling price high to low
    - 'discount': Discount percentage high to low
    - 'popular': By rating/review count
    """
    if sort_by == 'price_asc':
        return query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        return query.order_by(Product.price.desc())
    elif sort_by == 'oldest':
        return query.order_by(Product.created_at.asc())
    elif sort_by == 'discount':
        return query.order_by(Product.discount.desc())
    elif sort_by == 'popular':
        return query.order_by(Product.stock.desc())
    else:  # Default: 'newest'
        return query.order_by(Product.created_at.desc())


def algorithm_3_filter_products(query, category_id, min_price, max_price, in_stock_only, min_discount):
    """
    ALGORITHM 3: PRODUCT MULTI-ATTRIBUTE FILTERING ALGORITHM
    Explanation for Viva:
    Filters the SQL product dataset based on multiple independent attributes:
    1. Category ID match
    2. Minimum price bound (price >= min_price)
    3. Maximum price bound (price <= max_price)
    4. Inventory availability (stock > 0)
    5. Discount threshold (discount >= min_discount)
    """
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if in_stock_only:
        query = query.filter(Product.stock > 0)
    if min_discount is not None:
        query = query.filter(Product.discount >= min_discount)
    return query


def algorithm_4_calculate_cart(cart_items):
    """
    ALGORITHM 4 & 5: SHOPPING CART & DISCOUNT CALCULATION ALGORITHM
    Explanation for Viva:
    1. Iterates through each cart item and computes:
       item_total = product.price * item.quantity
    2. Sums item_totals to obtain 'subtotal'.
    3. Calculates potential promotional discount.
    4. Evaluates shipping threshold: Free shipping if subtotal >= ₹999, else ₹99.
    5. Computes final_amount = subtotal - discount + shipping.
    """
    subtotal = 0.0
    discount_amount = 0.0

    for item in cart_items:
        subtotal += item.product.price * item.quantity

    # Free shipping rule: orders over ₹999 get free delivery
    shipping_amount = 0.0 if (subtotal >= 999.0 or subtotal == 0) else 99.0
    final_amount = round(subtotal - discount_amount + shipping_amount, 2)

    return {
        'subtotal': round(subtotal, 2),
        'discount_amount': round(discount_amount, 2),
        'shipping_amount': round(shipping_amount, 2),
        'final_amount': final_amount
    }


def algorithm_6_recommend_related(product, limit=4):
    """
    ALGORITHM 6: RULE-BASED PRODUCT RECOMMENDATION ALGORITHM
    Explanation for Viva:
    Content-based recommendation logic:
    Finds products that belong to the SAME category as the current product,
    excluding the current product itself, ordered by stock availability and recency.
    """
    if not product or not product.category_id:
        return Product.query.filter(Product.id != product.id).limit(limit).all()

    related = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).order_by(Product.created_at.desc()).limit(limit).all()

    # Fallback if fewer related products found
    if len(related) < limit:
        extra = Product.query.filter(
            Product.id != product.id,
            ~Product.id.in_([p.id for p in related])
        ).limit(limit - len(related)).all()
        related.extend(extra)

    return related


def algorithm_7_order_tracking_steps(current_status):
    """
    ALGORITHM 8: ORDER STATUS PROGRESSION ALGORITHM
    Explanation for Viva:
    Defines the ordered chronological lifecycle stages of an order:
    1. Placed -> 2. Payment Confirmed -> 3. Order Confirmed -> 4. Processing -> 5. Shipped -> 6. Delivered
    Used by the tracking UI timeline to highlight completed vs pending steps.
    """
    all_steps = ['Placed', 'Payment Confirmed', 'Order Confirmed', 'Processing', 'Shipped', 'Delivered']
    
    if current_status == 'Cancelled':
        return [{'name': s, 'status': 'cancelled' if s == 'Placed' else 'inactive'} for s in all_steps]

    try:
        current_index = all_steps.index(current_status)
    except ValueError:
        current_index = 0

    timeline = []
    for idx, step in enumerate(all_steps):
        if idx < current_index:
            state = 'completed'
        elif idx == current_index:
            state = 'active'
        else:
            state = 'pending'
        timeline.append({'name': step, 'state': state})
    return timeline


# ===========================================================================
# ROUTES: AUTHENTICATION (REGISTER, LOGIN, LOGOUT)
# ===========================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User Registration:
    Requires: Name, Email, exactly 6-digit password, confirm password, Role (Buyer / Seller).
    Uses Werkzeug password hashing. Never stores plain passwords.
    """
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        role = request.form.get('role', 'buyer').strip().lower()

        # Validate fields
        if not name or not email or not password:
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')

        # Requirement: Exactly 6 characters / digits
        if len(password) != 6:
            flash('Password must be exactly 6 characters or digits long.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match. Please re-enter.', 'error')
            return render_template('register.html')

        if role not in ['buyer', 'seller']:
            role = 'buyer'

        # Check if email is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('login'))

        # Secure password hashing using Werkzeug
        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        # Automatically create cart for new user
        new_cart = Cart(user_id=new_user.id)
        db.session.add(new_cart)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User Login:
    Accepts Email + 6-digit password. Validates against hashed password in MySQL.
    """
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Please enter your email and password.', 'error')
            return render_template('login.html')

        # Validate 6-digit length constraint
        if len(password) != 6:
            flash('Password must be exactly 6 characters or digits.', 'error')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        # Check hash securely
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['role'] = user.role

            flash(f'Welcome back, {user.name}!', 'success')

            # Role-based landing redirects
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'seller':
                return redirect(url_for('seller_dashboard'))
            else:
                next_url = request.args.get('next')
                return redirect(next_url or url_for('index'))
        else:
            flash('Invalid email or 6-digit password. Try demo: 123456', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logs out current user and clears session."""
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('index'))


# ===========================================================================
# ROUTES: HOME & BROWSE PRODUCTS
# ===========================================================================

@app.route('/')
def index():
    """
    Home page showcasing hero banner, categories, featured products,
    new arrivals, best sellers, discount promotions, and reviews.
    """
    # Featured products: newest 8 items
    featured_products = Product.query.order_by(Product.created_at.desc()).limit(8).all()

    # New arrivals: first 4
    new_arrivals = Product.query.order_by(Product.created_at.desc()).limit(4).all()

    # Best sellers: products with high stock / high discounts
    best_sellers = Product.query.order_by(Product.discount.desc()).limit(4).all()

    # Recent customer reviews
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(3).all()

    return render_template(
        'index.html',
        featured_products=featured_products,
        new_arrivals=new_arrivals,
        best_sellers=best_sellers,
        recent_reviews=recent_reviews
    )


@app.route('/products')
def products():
    """
    Product Catalog Page:
    Supports Search, Multi-Filter (category, min/max price, in_stock, discount),
    and Sorting (newest, oldest, price_asc, price_desc, popular, discount).
    """
    search_query = request.args.get('search', '').strip()
    category_id = request.args.get('category', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    in_stock_only = request.args.get('in_stock') == '1'
    min_discount = request.args.get('min_discount', type=int)
    sort_by = request.args.get('sort', 'newest')

    # Step 1: Search using Algorithm 1
    query = algorithm_1_search_products(search_query)

    # Step 2: Filter using Algorithm 3
    query = algorithm_3_filter_products(
        query, category_id, min_price, max_price, in_stock_only, min_discount
    )

    # Step 3: Sort using Algorithm 2
    query = algorithm_2_sort_products(query, sort_by)

    product_list = query.all()

    # Wishlist IDs for the logged-in buyer to show active heart icons
    user_wishlist_ids = set()
    if 'user_id' in session:
        user_wishlist_ids = {
            w.product_id for w in Wishlist.query.filter_by(buyer_id=session['user_id']).all()
        }

    return render_template(
        'products.html',
        products=product_list,
        search_query=search_query,
        selected_category=category_id,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
        min_discount=min_discount,
        sort_by=sort_by,
        user_wishlist_ids=user_wishlist_ids
    )


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """
    Product details page:
    Shows large image, descriptions, pricing, stock, quantity selector,
    customer reviews, and related products via Algorithm 6.
    """
    product = Product.query.get_or_404(product_id)

    # Algorithm 6: Related product recommendations
    related_products = algorithm_6_recommend_related(product, limit=4)

    # Check if in wishlist
    in_wishlist = False
    if 'user_id' in session:
        in_wishlist = Wishlist.query.filter_by(
            buyer_id=session['user_id'], product_id=product.id
        ).first() is not None

    return render_template(
        'product.html',
        product=product,
        related_products=related_products,
        in_wishlist=in_wishlist
    )


# ===========================================================================
# ROUTES: REVIEWS & RATINGS
# ===========================================================================

@app.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    """Submits a customer rating (1-5) and review comment."""
    product = Product.query.get_or_404(product_id)
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()

    if not rating or rating < 1 or rating > 5:
        flash('Please select a valid star rating between 1 and 5.', 'error')
        return redirect(url_for('product_detail', product_id=product.id))

    new_review = Review(
        product_id=product.id,
        buyer_id=session['user_id'],
        rating=rating,
        comment=comment
    )
    db.session.add(new_review)
    db.session.commit()

    flash('Thank you! Your review has been added.', 'success')
    return redirect(url_for('product_detail', product_id=product.id))


# ===========================================================================
# ROUTES: SHOPPING CART
# ===========================================================================

@app.route('/cart')
@login_required
def cart():
    """Displays user's shopping cart with computed calculations."""
    user_cart = Cart.query.filter_by(user_id=session['user_id']).first()
    cart_items = user_cart.items if user_cart else []

    # Cart pricing calculation (Algorithm 4)
    totals = algorithm_4_calculate_cart(cart_items)

    return render_template('cart.html', cart_items=cart_items, totals=totals)


@app.route('/cart/add/<int:product_id>', methods=['POST', 'GET'])
@login_required
def add_to_cart(product_id):
    """Adds a product to the user's cart or increments quantity."""
    product = Product.query.get_or_404(product_id)

    if product.stock <= 0:
        flash('Sorry, this product is currently out of stock.', 'error')
        return redirect(request.referrer or url_for('products'))

    # Get or create cart for user
    user_cart = Cart.query.filter_by(user_id=session['user_id']).first()
    if not user_cart:
        user_cart = Cart(user_id=session['user_id'])
        db.session.add(user_cart)
        db.session.commit()

    # Requested quantity
    quantity = 1
    if request.method == 'POST':
        quantity = int(request.form.get('quantity', 1))
    else:
        quantity = int(request.args.get('quantity', 1))

    quantity = max(1, min(quantity, product.stock))

    # Check if product is already in cart
    existing_item = CartItem.query.filter_by(cart_id=user_cart.id, product_id=product.id).first()
    if existing_item:
        if existing_item.quantity + quantity > product.stock:
            existing_item.quantity = product.stock
            flash(f'Cart updated to maximum available stock ({product.stock}).', 'info')
        else:
            existing_item.quantity += quantity
            flash('Product quantity updated in cart.', 'success')
    else:
        new_item = CartItem(cart_id=user_cart.id, product_id=product.id, quantity=quantity)
        db.session.add(new_item)
        flash('Item added to your shopping cart!', 'success')

    db.session.commit()

    # If action was "Buy Now", redirect directly to checkout
    if request.form.get('buy_now') == '1':
        return redirect(url_for('checkout'))

    return redirect(request.referrer or url_for('cart'))


@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    """Updates quantity of an item in the shopping cart."""
    cart_item = CartItem.query.get_or_404(item_id)

    # Ensure this item belongs to the logged-in user
    if cart_item.cart.user_id != session['user_id']:
        abort(403)

    quantity = int(request.form.get('quantity', 1))
    if quantity <= 0:
        db.session.delete(cart_item)
        flash('Item removed from cart.', 'info')
    else:
        cart_item.quantity = min(quantity, cart_item.product.stock)
        flash('Cart updated.', 'success')

    db.session.commit()
    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    """Removes an item from the cart."""
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != session['user_id']:
        abort(403)

    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from your cart.', 'info')
    return redirect(url_for('cart'))


# ===========================================================================
# ROUTES: CHECKOUT & PAYMENT MODE SYSTEM
# ===========================================================================

@app.route('/checkout')
@login_required
def checkout():
    """
    Checkout page:
    Shows delivery details form, order items summary, and
    the 4 Payment Modes: COD, UPI, Credit/Debit Card, Net Banking.
    """
    user_cart = Cart.query.filter_by(user_id=session['user_id']).first()
    if not user_cart or not user_cart.items:
        flash('Your cart is empty. Add items before checking out.', 'warning')
        return redirect(url_for('products'))

    totals = algorithm_4_calculate_cart(user_cart.items)
    user = User.query.get(session['user_id'])

    return render_template(
        'checkout.html',
        cart_items=user_cart.items,
        totals=totals,
        user=user
    )


@app.route('/place-order', methods=['POST'])
@login_required
def place_order():
    """
    Places Order & Processes Simulated Payment:
    1. Validates delivery details and payment method (COD, UPI, CARD, NET_BANKING).
    2. Computes total amounts.
    3. Simulates transaction ID (e.g. TXN20261007...).
    4. Creates Order in orders table.
    5. Saves Payment in payments table.
    6. Adds initial OrderTracking milestones.
    7. Deducts inventory stock.
    8. Empties user's cart.
    9. Redirects to Payment Success confirmation page.
    """
    user_id = session['user_id']
    user_cart = Cart.query.filter_by(user_id=user_id).first()

    if not user_cart or not user_cart.items:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('products'))

    # Delivery form inputs
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    pincode = request.form.get('pincode', '').strip()

    # Payment inputs
    payment_method = request.form.get('payment_method', 'COD').upper()

    if not all([name, email, phone, address, city, state, pincode]):
        flash('Please fill in all delivery address fields.', 'error')
        return redirect(url_for('checkout'))

    if payment_method not in ['COD', 'UPI', 'CARD', 'NET_BANKING']:
        payment_method = 'COD'

    # Simulated Payment Verification & Transaction ID Generation
    if payment_method == 'COD':
        payment_status = 'Pending'
        transaction_id = 'N/A'
        order_initial_status = 'Placed'
    else:
        # Online Payment Simulation (UPI / CARD / NET_BANKING)
        payment_status = 'Success'
        # Unique timestamped demo transaction reference
        random_suffix = random.randint(1000, 9999)
        transaction_id = f"TXN{datetime.utcnow().strftime('%Y%m%d%H%M')}{random_suffix}"
        order_initial_status = 'Confirmed'

    # Pricing calculation
    totals = algorithm_4_calculate_cart(user_cart.items)

    # 1. Create Order
    new_order = Order(
        buyer_id=user_id,
        total_amount=totals['subtotal'],
        discount_amount=totals['discount_amount'],
        shipping_amount=totals['shipping_amount'],
        final_amount=totals['final_amount'],
        status=order_initial_status,
        payment_method=payment_method,
        payment_status=payment_status,
        transaction_id=transaction_id,
        delivery_name=name,
        delivery_email=email,
        delivery_phone=phone,
        delivery_address=address,
        delivery_city=city,
        delivery_state=state,
        delivery_pincode=pincode
    )
    db.session.add(new_order)
    db.session.flush()  # Populates new_order.id

    # 2. Add Order Items & Deduct Stock
    for item in user_cart.items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product.id,
            seller_id=item.product.seller_id,
            quantity=item.quantity,
            price=item.product.price
        )
        db.session.add(order_item)

        # Inventory reduction
        item.product.stock = max(0, item.product.stock - item.quantity)

    # 3. Create Payment record in 'payments' table
    payment_record = Payment(
        order_id=new_order.id,
        user_id=user_id,
        payment_method=payment_method,
        payment_status=payment_status,
        transaction_id=transaction_id,
        amount=totals['final_amount']
    )
    db.session.add(payment_record)

    # 4. Add Order Tracking milestones
    tracking_1 = OrderTracking(order_id=new_order.id, status='Placed')
    db.session.add(tracking_1)

    if payment_status == 'Success':
        tracking_2 = OrderTracking(order_id=new_order.id, status='Payment Confirmed')
        tracking_3 = OrderTracking(order_id=new_order.id, status='Order Confirmed')
        db.session.add(tracking_2)
        db.session.add(tracking_3)

    # 5. Empty user's cart
    CartItem.query.filter_by(cart_id=user_cart.id).delete()

    db.session.commit()

    flash('Order successfully placed!', 'success')
    return redirect(url_for('payment_success', order_id=new_order.id))


@app.route('/payment-success/<int:order_id>')
@login_required
def payment_success(order_id):
    """Displays payment receipt and confirmation banner."""
    order = Order.query.get_or_404(order_id)
    if order.buyer_id != session['user_id'] and session.get('role') != 'admin':
        abort(403)
    return render_template('payment_success.html', order=order)


# ===========================================================================
# ROUTES: BUYER ORDERS & ORDER TRACKING
# ===========================================================================

@app.route('/orders')
@login_required
def orders():
    """Lists order history for the logged-in buyer."""
    buyer_orders = Order.query.filter_by(
        buyer_id=session['user_id']
    ).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=buyer_orders)


@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    """
    Detailed Order View with:
    - Products, quantities, prices
    - Subtotal, discount, delivery, total
    - Payment mode, payment status, transaction ID
    - Chronological Tracking Timeline
    """
    order = Order.query.get_or_404(order_id)

    # Allow access only to the buyer, seller of products in order, or admin
    is_buyer = order.buyer_id == session['user_id']
    is_admin = session.get('role') == 'admin'
    is_seller = any(item.seller_id == session['user_id'] for item in order.items)

    if not (is_buyer or is_admin or is_seller):
        abort(403)

    # Algorithm 8: Generate timeline steps
    timeline_steps = algorithm_7_order_tracking_steps(order.status)

    return render_template(
        'order_detail.html',
        order=order,
        timeline_steps=timeline_steps
    )


# ===========================================================================
# ROUTES: WISHLIST & PROFILE
# ===========================================================================

@app.route('/wishlist')
@login_required
def wishlist():
    """Displays buyer's saved wishlist products."""
    user_wishlist = Wishlist.query.filter_by(buyer_id=session['user_id']).all()
    return render_template('wishlist.html', wishlist=user_wishlist)


@app.route('/wishlist/add/<int:product_id>')
@login_required
def add_to_wishlist(product_id):
    """Toggles / Adds product to wishlist."""
    product = Product.query.get_or_404(product_id)
    existing = Wishlist.query.filter_by(
        buyer_id=session['user_id'], product_id=product.id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash(f'Removed "{product.name}" from wishlist.', 'info')
    else:
        new_entry = Wishlist(buyer_id=session['user_id'], product_id=product.id)
        db.session.add(new_entry)
        db.session.commit()
        flash(f'Added "{product.name}" to wishlist!', 'success')

    return redirect(request.referrer or url_for('wishlist'))


@app.route('/wishlist/remove/<int:product_id>')
@login_required
def remove_from_wishlist(product_id):
    """Removes product from wishlist."""
    entry = Wishlist.query.filter_by(
        buyer_id=session['user_id'], product_id=product_id
    ).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
        flash('Removed from wishlist.', 'info')
    return redirect(url_for('wishlist'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management: view details, update name, change 6-digit password."""
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_info':
            new_name = request.form.get('name', '').strip()
            if new_name:
                user.name = new_name
                session['user_name'] = new_name
                db.session.commit()
                flash('Profile name updated successfully.', 'success')

        elif action == 'change_password':
            old_pass = request.form.get('old_password', '').strip()
            new_pass = request.form.get('password', '').strip()
            confirm_pass = request.form.get('confirm_password', '').strip()

            if not check_password_hash(user.password, old_pass):
                flash('Current password is incorrect.', 'error')
            elif len(new_pass) != 6:
                flash('New password must be exactly 6 characters or digits long.', 'error')
            elif new_pass != confirm_pass:
                flash('New passwords do not match.', 'error')
            else:
                user.password = generate_password_hash(new_pass)
                db.session.commit()
                flash('Password changed successfully!', 'success')

    recent_orders = Order.query.filter_by(
        buyer_id=user.id
    ).order_by(Order.created_at.desc()).limit(5).all()

    return render_template('profile.html', user=user, recent_orders=recent_orders)


# ===========================================================================
# ROUTES: SELLER DASHBOARD & MANAGEMENT
# ===========================================================================

@app.route('/seller')
@seller_required
def seller_dashboard():
    """
    Seller Dashboard:
    Metrics: Total Products, Total Orders, Total Sales, Total Inventory Stock.
    """
    seller_id = session['user_id']
    seller_products = Product.query.filter_by(seller_id=seller_id).all()

    # Calculate seller's sales and order stats
    seller_order_items = OrderItem.query.filter_by(seller_id=seller_id).all()
    order_ids = set(item.order_id for item in seller_order_items)

    total_sales = sum(item.price * item.quantity for item in seller_order_items)
    total_stock = sum(p.stock for p in seller_products)

    recent_orders = Order.query.filter(Order.id.in_(order_ids)).order_by(Order.created_at.desc()).limit(5).all() if order_ids else []

    return render_template(
        'seller/dashboard.html',
        products=seller_products,
        total_products=len(seller_products),
        total_orders=len(order_ids),
        total_sales=round(total_sales, 2),
        total_stock=total_stock,
        recent_orders=recent_orders
    )


@app.route('/seller/add-product', methods=['GET', 'POST'])
@seller_required
def seller_add_product():
    """Allows seller to create a new product."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float)
        original_price = request.form.get('original_price', type=float)
        discount = request.form.get('discount', type=int, default=0)
        stock = request.form.get('stock', type=int, default=10)
        image = request.form.get('image', '').strip()

        if not name or price is None:
            flash('Product name and price are required.', 'error')
            return render_template('seller/add_product.html')

        # Auto-compute discount percentage if original price is provided
        if original_price and original_price > price and not discount:
            discount = int(round(((original_price - price) / original_price) * 100))

        new_product = Product(
            seller_id=session['user_id'],
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            original_price=original_price or price,
            discount=discount,
            stock=stock,
            image=image or 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80'
        )
        db.session.add(new_product)
        db.session.commit()

        flash(f'Product "{name}" added successfully!', 'success')
        return redirect(url_for('seller_dashboard'))

    return render_template('seller/add_product.html')


@app.route('/seller/edit-product/<int:product_id>', methods=['GET', 'POST'])
@seller_required
def seller_edit_product(product_id):
    """Allows seller to update their own product."""
    product = Product.query.get_or_404(product_id)

    # Security check: Sellers cannot edit another seller's product
    if product.seller_id != session['user_id']:
        abort(403)

    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.description = request.form.get('description', '').strip()
        product.category_id = request.form.get('category_id', type=int)
        product.price = request.form.get('price', type=float)
        product.original_price = request.form.get('original_price', type=float)
        product.discount = request.form.get('discount', type=int, default=0)
        product.stock = request.form.get('stock', type=int, default=0)
        product.image = request.form.get('image', '').strip()

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('seller_dashboard'))

    return render_template('seller/edit_product.html', product=product)


@app.route('/seller/delete-product/<int:product_id>')
@seller_required
def seller_delete_product(product_id):
    """Allows seller to delete their own product."""
    product = Product.query.get_or_404(product_id)

    if product.seller_id != session['user_id']:
        abort(403)

    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully.', 'info')
    return redirect(url_for('seller_dashboard'))


@app.route('/seller/orders')
@seller_required
def seller_orders():
    """
    Displays orders containing the seller's products,
    showing customer name, payment mode, payment status, and order status.
    """
    seller_id = session['user_id']
    order_items = OrderItem.query.filter_by(seller_id=seller_id).all()
    order_ids = list(set(item.order_id for item in order_items))

    orders_list = Order.query.filter(Order.id.in_(order_ids)).order_by(Order.created_at.desc()).all() if order_ids else []

    return render_template('seller/orders.html', orders=orders_list)


@app.route('/seller/order/update-status/<int:order_id>', methods=['POST'])
@seller_required
def seller_update_order_status(order_id):
    """Allows seller to update the status of an order."""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')

    valid_statuses = ['Placed', 'Confirmed', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
    if new_status in valid_statuses:
        order.status = new_status
        # Log to tracking table
        tracking = OrderTracking(order_id=order.id, status=new_status)
        db.session.add(tracking)
        db.session.commit()
        flash(f'Order #{order.id} status updated to "{new_status}".', 'success')

    return redirect(url_for('seller_orders'))


# ===========================================================================
# ROUTES: ADMIN DASHBOARD & MANAGEMENT
# ===========================================================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """
    Admin Dashboard:
    - User stats: Total users, buyers, sellers
    - Catalog stats: Total products, orders
    - Financial stats: Total revenue
    - Payment summary: COD, UPI, Card, Net Banking count, Success vs Pending
    """
    total_users = User.query.count()
    total_buyers = User.query.filter_by(role='buyer').count()
    total_sellers = User.query.filter_by(role='seller').count()
    total_products = Product.query.count()
    total_orders = Order.query.count()

    total_revenue = db.session.query(db.func.sum(Order.final_amount)).scalar() or 0.0

    # Payment statistics
    upi_orders = Order.query.filter_by(payment_method='UPI').count()
    card_orders = Order.query.filter_by(payment_method='CARD').count()
    net_orders = Order.query.filter_by(payment_method='NET_BANKING').count()
    cod_orders = Order.query.filter_by(payment_method='COD').count()

    successful_payments = Order.query.filter_by(payment_status='Success').count()
    pending_payments = Order.query.filter_by(payment_status='Pending').count()

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(6).all()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_buyers=total_buyers,
        total_sellers=total_sellers,
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=round(total_revenue, 2),
        upi_orders=upi_orders,
        card_orders=card_orders,
        net_orders=net_orders,
        cod_orders=cod_orders,
        successful_payments=successful_payments,
        pending_payments=pending_payments,
        recent_orders=recent_orders
    )


@app.route('/admin/users')
@admin_required
def admin_users():
    """Lists all registered users with option to delete."""
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list)


@app.route('/admin/user/delete/<int:user_id>')
@admin_required
def admin_delete_user(user_id):
    """Deletes a user account (excluding the active admin)."""
    if user_id == session['user_id']:
        flash('You cannot delete your own active administrator account.', 'error')
        return redirect(url_for('admin_users'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{user.name}" has been removed.', 'info')
    return redirect(url_for('admin_users'))


@app.route('/admin/products')
@admin_required
def admin_products():
    """Lists all products across all sellers."""
    products_list = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products_list)


@app.route('/admin/product/delete/<int:product_id>')
@admin_required
def admin_delete_product(product_id):
    """Admin product deletion."""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{product.name}" has been deleted.', 'info')
    return redirect(url_for('admin_products'))


@app.route('/admin/orders')
@admin_required
def admin_orders():
    """Displays all system orders with payment and status changer."""
    orders_list = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders_list)


@app.route('/admin/order/update-status/<int:order_id>', methods=['POST'])
@admin_required
def admin_update_order_status(order_id):
    """Allows admin to update order lifecycle status."""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status:
        order.status = new_status
        tracking = OrderTracking(order_id=order.id, status=new_status)
        db.session.add(tracking)
        db.session.commit()
        flash(f'Order #{order.id} status updated to "{new_status}".', 'success')
    return redirect(url_for('admin_orders'))


@app.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def admin_categories():
    """Allows admin to manage categories."""
    if request.method == 'POST':
        category_name = request.form.get('name', '').strip()
        if category_name:
            existing = Category.query.filter_by(name=category_name).first()
            if not existing:
                new_cat = Category(name=category_name)
                db.session.add(new_cat)
                db.session.commit()
                flash(f'Category "{category_name}" added successfully.', 'success')
            else:
                flash('Category already exists.', 'warning')
        return redirect(url_for('admin_categories'))

    categories_list = Category.query.all()
    return render_template('admin/categories.html', categories=categories_list)


@app.route('/admin/category/delete/<int:cat_id>')
@admin_required
def admin_delete_category(cat_id):
    """Deletes a category."""
    category = Category.query.get_or_404(cat_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted.', 'info')
    return redirect(url_for('admin_categories'))


# ===========================================================================
# ERROR HANDLERS
# ===========================================================================

@app.errorhandler(404)
def not_found_error(error):
    """Friendly 404 Page Not Found error handler."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Friendly 500 Server Error error handler."""
    db.session.rollback()
    return render_template('500.html'), 500


# ===========================================================================
# AUTOMATIC DATABASE INITIALIZATION & SAMPLE SEEDER HELPER
# ===========================================================================
def auto_init_database():
    """
    Checks if MySQL tables exist and creates them if needed.
    Also seeds initial admin, seller, buyer and sample products
    if the database is empty, ensuring the app runs out-of-the-box.
    """
    with app.app_context():
        try:
            db.create_all()

            # Seed default users if users table is empty
            if User.query.count() == 0:
                demo_hash = generate_password_hash('123456')
                admin = User(name='Admin User', email='admin@foreverr.com', password=demo_hash, role='admin')
                seller = User(name='Aria Seller', email='seller@foreverr.com', password=demo_hash, role='seller')
                buyer = User(name='Sophia Buyer', email='buyer@foreverr.com', password=demo_hash, role='buyer')
                db.session.add_all([admin, seller, buyer])
                db.session.commit()

                # Seed categories
                categories = [
                    Category(name="Women's Jewellery"),
                    Category(name="Personalised Gifts"),
                    Category(name="Pet Accessories"),
                    Category(name="Accessories"),
                    Category(name="Best Sellers"),
                    Category(name="New Arrivals"),
                ]
                db.session.add_all(categories)
                db.session.commit()

                # Seed sample products
                sample_products = [
                    Product(
                        seller_id=seller.id, category_id=1,
                        name='Classic Heart Pendant',
                        description='An 18k gold-plated heart pendant suspended on an ultra-delicate chain. Perfect for effortless daily sophistication.',
                        price=1299.00, original_price=1699.00, discount=24, stock=25,
                        image='https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80'
                    ),
                    Product(
                        seller_id=seller.id, category_id=2,
                        name='Personalised Name Bracelet',
                        description='Custom-engraved stainless steel cuff bracelet with high-polish finish. Handcrafted with precision for memorable gifting.',
                        price=999.00, original_price=1499.00, discount=33, stock=18,
                        image='https://images.unsplash.com/photo-1611591475819-79b8b73c2c31?auto=format&fit=crop&w=800&q=80'
                    ),
                    Product(
                        seller_id=seller.id, category_id=1,
                        name='Baroque Pearl Earrings',
                        description='Natural freshwater baroque pearls paired with hypoallergenic golden hoops. Timeless elegance suited for all occasions.',
                        price=1499.00, original_price=1999.00, discount=25, stock=12,
                        image='https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&q=80'
                    ),
                    Product(
                        seller_id=seller.id, category_id=3,
                        name='Pet Name Tag',
                        description='Durable solid brass pet ID tag custom-engraved with your pet name and contact number. Water-resistant and rust-proof.',
                        price=499.00, original_price=699.00, discount=29, stock=40,
                        image='https://images.unsplash.com/photo-1548767797-d8c844163c4c?auto=format&fit=crop&w=800&q=80'
                    ),
                    Product(
                        seller_id=seller.id, category_id=1,
                        name='Minimal Chain Necklace',
                        description='Sleek paperclip herringbone link chain crafted in premium surgical titanium steel with 18K gold luster.',
                        price=899.00, original_price=1199.00, discount=25, stock=30,
                        image='https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?auto=format&fit=crop&w=800&q=80'
                    ),
                    Product(
                        seller_id=seller.id, category_id=2,
                        name='Personalised Leather Keychain',
                        description='Full-grain Italian vegan leather keychain embossed with personalized initials and brass carabiner clasp.',
                        price=599.00, original_price=799.00, discount=25, stock=35,
                        image='https://images.unsplash.com/photo-1622434641406-a158123450f9?auto=format&fit=crop&w=800&q=80'
                    ),
                    Product(
                        seller_id=seller.id, category_id=4,
                        name='Celestial Charm Bracelet',
                        description='Delicate charm bracelet adorned with starbursts and crescent moons, encrusted with shimmering cubic zirconia.',
                        price=1199.00, original_price=1599.00, discount=25, stock=15,
                        image='https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&q=80'
                    ),
                    Product(
                        seller_id=seller.id, category_id=3,
                        name='Velvet Pet Collar with Bow',
                        description='Ultra-soft emerald velvet collar with rose gold alloy buckle and removable bow tie for your beloved furry friend.',
                        price=749.00, original_price=999.00, discount=25, stock=20,
                        image='https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=800&q=80'
                    ),
                ]
                db.session.add_all(sample_products)
                db.session.commit()

                # Seed sample review
                rev = Review(
                    product_id=1, buyer_id=buyer.id, rating=5,
                    comment='Absolutely gorgeous! The heart pendant shines brilliantly and the chain is sturdy yet delicate.'
                )
                db.session.add(rev)
                db.session.commit()
                print(">>> [Foreverr] Sample data successfully initialized in MySQL database.")
        except Exception as e:
            # If MySQL is not currently running, app will still import cleanly
            print(f">>> [Foreverr] Database init notice: {e}")


# ---------------------------------------------------------------------------
# MAIN EXECUTION ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    auto_init_database()
    print("=================================================================")
    print(" FOREVERR E-COMMERCE SERVER RUNNING")
    print(" Access at: http://127.0.0.1:5000")
    print("=================================================================")
    app.run(debug=True, host='127.0.0.1', port=5000)
