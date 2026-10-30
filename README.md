# FOREVERR – E-Commerce Web Application
### TYCS College Mini-Project (Flask + MySQL)

**Project Title:** Foreverr – An E-Commerce Web Application for Online Shopping, Personalized Products, and Product Management.  
**Inspiration:** Elegant, minimal, premium jewellery & personalized gifting store inspired by modern artisanal boutiques like [aalmari.in](https://aalmari.in/).  
**Tech Stack:** Python (Flask), MySQL, PyMySQL, Flask-SQLAlchemy, HTML5, CSS3, JavaScript.

---

## 📖 Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features by Role](#key-features-by-role)
3. [Architecture & MySQL Connection Flow](#architecture--mysql-connection-flow)
4. [File & Directory Structure](#file--directory-structure)
5. [Prerequisites](#prerequisites)
6. [Step-by-Step Installation & Setup](#step-by-step-installation--setup)
7. [How to Connect MySQL Workbench](#how-to-connect-mysql-workbench)
8. [Testing Guide (Buyer, Seller, Admin, & 4 Payment Modes)](#testing-guide)
9. [The 8 Core Algorithms for Viva Voce](#the-8-core-algorithms-for-viva-voce)
10. [Database Verification Queries](#database-verification-queries)

---

## 1. Project Overview
**Foreverr** is a complete, lightweight, production-grade e-commerce web application developed specifically for a TYCS college mini-project. It avoids overly complex microservices, Docker, React, or MongoDB, while demonstrating clean Model-View-Controller (MVC) software principles with secure user sessions, role-based authorization, dynamic multi-attribute filtering, custom search matching, and a simulated 4-mode checkout payment processing engine.

---

## 2. Key Features by Role

### 🛍️ Buyers
- **Authentication:** Registration & Login with Email and secure **6-digit password** (Werkzeug hashed).
- **Product Discovery:** Keyword search, multi-attribute filtering (Category, Price range, In-stock, Discounts), and sorting (Newest, Oldest, Price Low-High, Price High-Low, Discount, Popularity).
- **Product Detail:** High-resolution image preview, discount calculator, stock availability, customer reviews, dynamic quantity picker, and related product recommendations.
- **Cart & Wishlist:** Real-time item total calculation, automatic free shipping threshold (orders > ₹999), add/remove/update items.
- **Checkout & Simulated Payments:** Support for **Cash on Delivery (COD)**, **UPI**, **Credit/Debit Card**, and **Net Banking** with real-time UI switching.
- **Order Tracking:** Chronological order lifecycle tracking timeline (`Placed` → `Payment Confirmed` → `Order Confirmed` → `Processing` → `Shipped` → `Delivered`).
- **Product Reviews:** Submit 1 to 5-star ratings and textual feedback with dynamic average rating calculation.
- **Profile:** Manage full name, change 6-digit password, and review previous order receipts.

### 🏪 Sellers
- **Seller Dashboard:** Metric overview (Listed Products, Total Orders, Total Sales Revenue, Inventory Stock).
- **Product Management:** Add new products (with category, pricing, discount %, stock, and image URL preview), edit existing listings, and delete own listings.
- **Order Management:** View orders containing the seller's products, customer shipping details, payment method, payment status, and update the order lifecycle state.

### 🛡️ Admin
- **Admin Dashboard:** Platform-wide metrics (Total users, buyers, sellers, products, orders, gross revenue).
- **Payment Reconciliation Summary:** Detailed revenue and count breakdown for UPI, Cards, Net Banking, and COD orders, plus Successful vs Pending tallies.
- **Catalog & User Control:** View and delete user accounts, remove obsolete products, change order statuses, and add/delete product categories.

---

## 3. Architecture & MySQL Connection Flow

### How the Website Connects to MySQL
```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌───────────────┐         ┌─────────────┐         ┌───────────────────────┐
│ Browser  │ ──────> │   HTML   │ ──────> │  Flask   │ ──────> │  SQLAlchemy   │ ──────> │   PyMySQL   │ ──────> │ MySQL Server/Workbench│
│ (Client) │ <────── │ (Jinja2) │ <────── │ (Python) │ <────── │     (ORM)     │ <────── │ (Connector) │ <────── │  (foreverr database)  │
└──────────┘         └──────────┘         └──────────┘         └───────────────┘         └─────────────┘         └───────────────────────┘
```

1. **Browser:** The user opens the web page or submits a form.
2. **HTML (Jinja2):** The template captures user inputs and sends an HTTP GET/POST request.
3. **Flask (Python):** `app.py` handles the route, validates input, and enforces role security.
4. **Flask-SQLAlchemy (ORM):** Translates Python objects and queries (e.g., `Product.query.all()`) into SQL statements.
5. **PyMySQL:** The pure-Python database driver that sends TCP packets to the MySQL server on port 3306.
6. **MySQL Server:** Executes queries against the `foreverr` relational database and returns results.

---

## 4. File & Directory Structure

```
Foreverr/
│
├── app.py                     # Main Flask application & routes (all 8 algorithms)
├── database.py                # Flask-SQLAlchemy DB models (11 tables)
├── config.py                  # Database & session configuration
├── requirements.txt           # Python package dependencies
├── .env.example               # MySQL environment template
├── database.sql               # MySQL database script (schema & sample data)
├── README.md                  # Detailed documentation & viva guide
│
├── templates/                 # HTML5 Jinja2 Templates
│   ├── base.html              # Base layout with navbar, footer, notifications
│   ├── index.html             # Luxury homepage (Hero, Categories, Reviews)
│   ├── login.html             # Login with 6-digit password validation
│   ├── register.html          # Registration form (Buyer/Seller selection)
│   ├── products.html          # Shop page (Search, Filters, Sort)
│   ├── product.html           # Product details, reviews, related products
│   ├── cart.html              # Shopping cart with quantity and price breakdown
│   ├── checkout.html          # Checkout with 4 dynamic payment modes
│   ├── payment_success.html   # Simulated payment confirmation receipt
│   ├── orders.html            # Buyer order history
│   ├── order_detail.html      # Order tracking timeline & invoice details
│   ├── profile.html           # User profile & 6-digit password update
│   ├── wishlist.html          # Saved favorite products
│   ├── 404.html               # 404 Not Found error page
│   ├── 500.html               # 500 Server Error page
│   │
│   ├── seller/
│   │   ├── dashboard.html     # Seller metrics & product table
│   │   ├── add_product.html   # Add product form with image preview
│   │   ├── edit_product.html  # Edit product form
│   │   └── orders.html        # Seller order status updates
│   │
│   └── admin/
│       ├── dashboard.html     # Admin stats & payment breakdown
│       ├── users.html         # User list & delete controls
│       ├── products.html      # Catalog list & delete controls
│       ├── orders.html        # Platform-wide order manager
│       └── categories.html    # Add/delete product categories
│
└── static/
    ├── css/
    │   └── style.css          # Luxury Emerald (#315C45) & Ivory (#F7F3E8) theme
    ├── js/
    │   └── script.js          # Dynamic payment mode switcher, validations, quantity +/-
    └── images/                # Local asset storage directory
```

---

## 5. Prerequisites

Before running the project, make sure you have installed:
1. **Python 3.8+** ([python.org](https://www.python.org/downloads/)) — Ensure "Add Python to PATH" is checked during installation.
2. **VS Code** ([code.visualstudio.com](https://code.visualstudio.com/))
3. **MySQL Community Server & MySQL Workbench** ([dev.mysql.com](https://dev.mysql.com/downloads/installer/))

---

## 6. Step-by-Step Installation & Setup

### Step 1: Open Project in VS Code
Open VS Code, select **File > Open Folder...**, and select the `Foreverr` folder.

### Step 2: Create Python Virtual Environment
Open the integrated terminal in VS Code (`Ctrl + ~`) and run:
```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment
- **Windows (Command Prompt / PowerShell):**
  ```powershell
  venv\Scripts\activate
  ```
*(You will see `(venv)` appear at the beginning of your terminal prompt).*

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Configure Your MySQL Password
1. In the `Foreverr` root folder, create a new file called `.env` (or copy `.env.example` to `.env`).
2. Add your MySQL root password:
   ```env
   DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/foreverr
   SECRET_KEY=foreverr-college-project-secret-key-2026
   ```
   *Replace `YOUR_PASSWORD` with your actual MySQL password (e.g. `root`, `1234`, `admin`).*

---

## 7. How to Connect MySQL Workbench

1. Launch **MySQL Workbench**.
2. Click on your local instance (e.g., `Local instance MySQL80`) and enter your password.
3. In MySQL Workbench, click **File > Open SQL Script...** and select `database.sql` from the `Foreverr` folder.
4. Click the ⚡ **Execute** (lightning bolt) icon to run the script.
5. In the left **Schemas** pane, right-click and click **Refresh All**. You will see the `foreverr` database with all 11 tables populated with sample data!

---

## 8. Run the Application

In your terminal with `(venv)` active:
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 9. Testing Guide

### Pre-loaded Demo Accounts (Password: `123456`)
| Role | Email | 6-Digit Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Buyer** | `buyer@foreverr.com` | `123456` | Shop, Cart, Wishlist, 4-Mode Checkout, Orders, Reviews |
| **Seller** | `seller@foreverr.com` | `123456` | Seller Dashboard, Add/Edit/Delete Products, Manage Orders |
| **Admin** | `admin@foreverr.com` | `123456` | Admin Dashboard, Payment Summary, Manage Users & Categories |

### Testing Payment Modes:
1. Log in as `buyer@foreverr.com`.
2. Add any piece to your cart and click **Proceed to Checkout**.
3. Fill delivery details and test the payment selector:
   - **Cash on Delivery (COD):** Notice the order gets marked as `Payment Status: Pending`, `Transaction ID: N/A`.
   - **UPI:** Enter a UPI ID (e.g., `buyer@okhdfcbank`). Notice simulated `Payment Status: Success` and an instant `TXN2026...` transaction reference generated!
   - **Credit/Debit Card:** Enter card details (`XXXX XXXX XXXX 1234`, Expiry, CVV). Generates simulated instant success receipt.
   - **Net Banking:** Select your bank (e.g., HDFC Bank or SBI) and place order.
4. View the resulting order in **My Orders** and open **View Details & Tracking** to inspect the timeline!

---

## 10. The 8 Core Algorithms for Viva Voce

Here is the exact explanation of all 8 algorithms used in `app.py` for your college examiner:

1. **Algorithm 1: Token/Keyword Matching Search Algorithm**
   - *Logic:* Splits user query string by spaces into lowercase tokens. Searches across `Product.name`, `Product.description`, and joined `Category.name` using SQL `ILIKE` operators combined with `db.or_`.

2. **Algorithm 2: Product Sorting Algorithm**
   - *Logic:* Translates user query parameters (`sort=price_asc`, `sort=discount`, `sort=newest`) into corresponding SQL `order_by()` clauses (`Product.price.asc()`, `Product.discount.desc()`).

3. **Algorithm 3: Multi-Attribute Filtering Algorithm**
   - *Logic:* Dynamically filters the product query by category, minimum/maximum price boundaries, stock availability (`stock > 0`), and minimum discount percentages.

4. **Algorithm 4: Shopping Cart Calculation Algorithm**
   - *Logic:* Iterates through all items in the user's active cart. Computes `item_total = price * quantity` and sums them to obtain `subtotal`.

5. **Algorithm 5: Discount & Free Shipping Calculation Algorithm**
   - *Logic:* Computes promotional savings. Applies a threshold conditional: If `subtotal >= 999`, delivery is `0` (Free Shipping); otherwise, a flat `₹99` delivery fee is added. `final_amount = subtotal - discount + shipping`.

6. **Algorithm 6: Rule-Based Content Recommendation Algorithm**
   - *Logic:* Content-based filtering that retrieves other products matching the same `category_id` as the currently viewed product, excluding the product itself.

7. **Algorithm 7: Rating & Review Averaging Algorithm**
   - *Logic:* Calculates the arithmetic mean of customer review ratings:
     $$\text{Average Rating} = \frac{\sum \text{ratings}}{\text{Total number of reviews}}$$
     Rounded to 1 decimal place.

8. **Algorithm 8: Order Status Progression Algorithm**
   - *Logic:* Maps the linear status lifecycle (`Placed` → `Payment Confirmed` → `Order Confirmed` → `Processing` → `Shipped` → `Delivered`) to determine which timeline nodes are marked as completed, active, or pending on the customer tracking screen.

---

## 11. Database Verification Queries

Open MySQL Workbench and run these queries to inspect the data during your viva:
```sql
USE foreverr;

-- View all registered users
SELECT id, name, email, role, created_at FROM users;

-- View all listed products
SELECT id, name, price, stock, discount FROM products;

-- View customer orders and payment modes
SELECT id, buyer_id, final_amount, status, payment_method, payment_status, transaction_id FROM orders;

-- View payments transaction table
SELECT payment_id, order_id, payment_method, payment_status, transaction_id, amount FROM payments;

-- View customer reviews and ratings
SELECT id, product_id, buyer_id, rating, comment FROM reviews;
```

---
*Created with ❤️ for TYCS College Mini-Project Submission.*
