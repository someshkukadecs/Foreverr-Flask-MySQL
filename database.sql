-- =============================================================================
-- FOREVERR E-COMMERCE DATABASE SCRIPT
-- Compatible with MySQL 5.7+ and MySQL 8.0+ / MySQL Workbench
-- =============================================================================

-- Step 1: Create Database
CREATE DATABASE IF NOT EXISTS foreverr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE foreverr;

-- Step 2: Drop existing tables if re-running script (in proper foreign key dependency order)
DROP TABLE IF EXISTS order_tracking;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS wishlist;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- =============================================================================
-- 1. USERS TABLE
-- Stores Buyers, Sellers, and Admins
-- =============================================================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('buyer', 'seller', 'admin') NOT NULL DEFAULT 'buyer',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =============================================================================
-- 2. CATEGORIES TABLE
-- Stores Product Categories
-- =============================================================================
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- =============================================================================
-- 3. PRODUCTS TABLE
-- Stores Product Catalog details
-- =============================================================================
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    category_id INT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    original_price DECIMAL(10, 2) NULL,
    discount INT DEFAULT 0,
    stock INT NOT NULL DEFAULT 10,
    image VARCHAR(500) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_category (category_id),
    INDEX idx_seller (seller_id)
) ENGINE=InnoDB;

-- =============================================================================
-- 4. CART TABLE
-- Active shopping cart for each user
-- =============================================================================
CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- 5. CART ITEMS TABLE
-- Individual items inside a user's cart
-- =============================================================================
CREATE TABLE cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (cart_id) REFERENCES cart(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY uq_cart_product (cart_id, product_id)
) ENGINE=InnoDB;

-- =============================================================================
-- 6. ORDERS TABLE
-- Customer placed orders with payment status
-- =============================================================================
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    shipping_amount DECIMAL(10, 2) DEFAULT 0.00,
    final_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Placed',
    payment_method VARCHAR(30) NOT NULL DEFAULT 'COD',
    payment_status VARCHAR(30) NOT NULL DEFAULT 'Pending',
    transaction_id VARCHAR(60) NOT NULL DEFAULT 'N/A',
    delivery_name VARCHAR(100) NULL,
    delivery_email VARCHAR(120) NULL,
    delivery_phone VARCHAR(20) NULL,
    delivery_address TEXT NULL,
    delivery_city VARCHAR(60) NULL,
    delivery_state VARCHAR(60) NULL,
    delivery_pincode VARCHAR(20) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- 7. ORDER ITEMS TABLE
-- Line items associated with an order
-- =============================================================================
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NULL,
    seller_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- 8. PAYMENTS TABLE
-- Payment transactions for checkout simulation
-- =============================================================================
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    user_id INT NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    payment_status VARCHAR(30) NOT NULL,
    transaction_id VARCHAR(60) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- 9. REVIEWS TABLE
-- Product ratings (1-5 stars) and comments
-- =============================================================================
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    buyer_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- 10. WISHLIST TABLE
-- Saved favorite products for buyers
-- =============================================================================
CREATE TABLE wishlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,
    product_id INT NOT NULL,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_wishlist (buyer_id, product_id)
) ENGINE=InnoDB;

-- =============================================================================
-- 11. ORDER TRACKING TABLE
-- Step-by-step timeline updates for order tracking
-- =============================================================================
CREATE TABLE order_tracking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- =============================================================================
-- SAMPLE DATA INSERTION
-- Password for all default demo accounts is: 123456
-- Werkzeug scrypt hash used:
-- scrypt:32768:8:1$3XYImZf5vannBtAB$6ed21258888d9fd1a25f0e5bea754e8a9b0a73bfdc46d38fc73a008f6825ea0aaf26ebfaef5e74d43379e4b6e920ff9b3b8244138eaf832785aaeab5488ae9a7
-- =============================================================================

INSERT INTO users (id, name, email, password, role) VALUES
(1, 'Admin User', 'admin@foreverr.com', 'scrypt:32768:8:1$3XYImZf5vannBtAB$6ed21258888d9fd1a25f0e5bea754e8a9b0a73bfdc46d38fc73a008f6825ea0aaf26ebfaef5e74d43379e4b6e920ff9b3b8244138eaf832785aaeab5488ae9a7', 'admin'),
(2, 'Aria Seller', 'seller@foreverr.com', 'scrypt:32768:8:1$3XYImZf5vannBtAB$6ed21258888d9fd1a25f0e5bea754e8a9b0a73bfdc46d38fc73a008f6825ea0aaf26ebfaef5e74d43379e4b6e920ff9b3b8244138eaf832785aaeab5488ae9a7', 'seller'),
(3, 'Sophia Buyer', 'buyer@foreverr.com', 'scrypt:32768:8:1$3XYImZf5vannBtAB$6ed21258888d9fd1a25f0e5bea754e8a9b0a73bfdc46d38fc73a008f6825ea0aaf26ebfaef5e74d43379e4b6e920ff9b3b8244138eaf832785aaeab5488ae9a7', 'buyer');

INSERT INTO categories (id, name) VALUES
(1, "Women's Jewellery"),
(2, "Personalised Gifts"),
(3, "Pet Accessories"),
(4, "Accessories"),
(5, "Best Sellers"),
(6, "New Arrivals");

INSERT INTO products (id, seller_id, category_id, name, description, price, original_price, discount, stock, image) VALUES
(1, 2, 1, 'Classic Heart Pendant', 'An 18k gold-plated heart pendant suspended on an ultra-delicate chain. Perfect for effortless daily sophistication.', 1299.00, 1699.00, 24, 25, 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&q=80'),
(2, 2, 2, 'Personalised Name Bracelet', 'Custom-engraved stainless steel cuff bracelet with high-polish finish. Handcrafted with precision for memorable gifting.', 999.00, 1499.00, 33, 18, 'https://images.unsplash.com/photo-1611591475819-79b8b73c2c31?auto=format&fit=crop&w=800&q=80'),
(3, 2, 1, 'Baroque Pearl Earrings', 'Natural freshwater baroque pearls paired with hypoallergenic golden hoops. Timeless elegance suited for all occasions.', 1499.00, 1999.00, 25, 12, 'https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&q=80'),
(4, 2, 3, 'Pet Name Tag', 'Durable solid brass pet ID tag custom-engraved with your pet name and contact number. Water-resistant and rust-proof.', 499.00, 699.00, 29, 40, 'https://images.unsplash.com/photo-1548767797-d8c844163c4c?auto=format&fit=crop&w=800&q=80'),
(5, 2, 1, 'Minimal Chain Necklace', 'Sleek paperclip herringbone link chain crafted in premium surgical titanium steel with 18K gold luster.', 899.00, 1199.00, 25, 30, 'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?auto=format&fit=crop&w=800&q=80'),
(6, 2, 2, 'Personalised Leather Keychain', 'Full-grain Italian vegan leather keychain embossed with personalized initials and brass carabiner clasp.', 599.00, 799.00, 25, 35, 'https://images.unsplash.com/photo-1622434641406-a158123450f9?auto=format&fit=crop&w=800&q=80'),
(7, 2, 4, 'Celestial Charm Bracelet', 'Delicate charm bracelet adorned with starbursts and crescent moons, encrusted with shimmering cubic zirconia.', 1199.00, 1599.00, 25, 15, 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&q=80'),
(8, 2, 3, 'Velvet Pet Collar with Bow', 'Ultra-soft emerald velvet collar with rose gold alloy buckle and removable bow tie for your beloved furry friend.', 749.00, 999.00, 25, 20, 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=800&q=80');

INSERT INTO reviews (product_id, buyer_id, rating, comment) VALUES
(1, 3, 5, 'Absolutely gorgeous! The heart pendant shines brilliantly and the chain is sturdy yet delicate.'),
(2, 3, 5, 'The custom engraving was so neat and crisp. It made an amazing birthday present!'),
(3, 3, 4, 'Very elegant pearls, feels premium and luxurious on the ears.');

-- Sample Demo Order
INSERT INTO orders (id, buyer_id, total_amount, discount_amount, shipping_amount, final_amount, status, payment_method, payment_status, transaction_id, delivery_name, delivery_email, delivery_phone, delivery_address, delivery_city, delivery_state, delivery_pincode) VALUES
(1001, 3, 2298.00, 0.00, 0.00, 2298.00, 'Confirmed', 'UPI', 'Success', 'TXN202610071234', 'Sophia Buyer', 'buyer@foreverr.com', '9876543210', '12 Rosewood Apartments, Marine Drive', 'Mumbai', 'Maharashtra', '400020');

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price) VALUES
(1001, 1, 2, 1, 1299.00),
(1001, 2, 2, 1, 999.00);

INSERT INTO payments (payment_id, order_id, user_id, payment_method, payment_status, transaction_id, amount) VALUES
(1, 1001, 3, 'UPI', 'Success', 'TXN202610071234', 2298.00);

INSERT INTO order_tracking (order_id, status) VALUES
(1001, 'Order Placed'),
(1001, 'Payment Confirmed'),
(1001, 'Order Confirmed');
