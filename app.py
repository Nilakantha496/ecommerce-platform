import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Product, Order, OrderItem
import stripe

load_dotenv()

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_put_your_stripe_secret_key_here')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-ecommerce-key-123')

# Check for Vercel Postgres / Supabase URL
database_url = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')
if not database_url:
    if os.environ.get('VERCEL') == '1':
        database_url = 'sqlite:////tmp/ecommerce.db'
    else:
        database_url = 'sqlite:///ecommerce.db'

if database_url.startswith("postgres://") or database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgres://", "postgresql+pg8000://", 1)
    database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.before_request
def initialize_database():
    if not hasattr(app, '_db_initialized'):
        db.create_all()
        app._db_initialized = True

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- VIEWS ---

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/cart')
def cart():
    # Cart logic via session or local storage
    # We will use local storage on frontend, so this view just renders the cart page
    return render_template('cart.html')

@app.route('/checkout')
@login_required
def checkout():
    return render_template('checkout.html')

@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('index'))
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    all_products = Product.query.all()
    return render_template('admin.html', orders=all_orders, products=all_products)

@app.route('/admin/add_product', methods=['POST'])
@login_required
def add_product():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    name = request.form.get('name')
    price = request.form.get('price')
    category = request.form.get('category')
    stock = request.form.get('stock')
    image_url = request.form.get('image_url', '')
    description = request.form.get('description')
    
    try:
        new_product = Product(
            name=name,
            price=float(price),
            category=category,
            stock=int(stock),
            image_url=image_url,
            description=description
        )
        db.session.add(new_product)
        db.session.commit()
        flash(f'Product "{name}" added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding product: {str(e)}', 'danger')
        
    return redirect(url_for('admin'))

# --- AUTH ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists. Please login.', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# --- API ROUTES ---

@app.route('/api/create-checkout-session', methods=['POST'])
@login_required
def api_create_checkout_session():
    data = request.json
    cart_items = data.get('cart', [])
    
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400
        
    total_amount = 0
    order_items = []
    line_items = []
    
    # Calculate total and verify stock
    for item in cart_items:
        product = Product.query.get(item['id'])
        if not product:
            return jsonify({'error': f'Product {item["id"]} not found'}), 404
        if product.stock < item['quantity']:
            return jsonify({'error': f'Insufficient stock for {product.name}'}), 400
            
        price = product.price
        total_amount += price * item['quantity']
        
        # We DO NOT decrement stock here. We do it upon successful payment.
        
        order_item = OrderItem(
            product_id=product.id,
            quantity=item['quantity'],
            price_at_purchase=price
        )
        order_items.append(order_item)
        
        # Stripe line item
        line_items.append({
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': int(price * 100), # Stripe expects paise for INR
            },
            'quantity': item['quantity'],
        })
        
    # Create order in Pending state
    new_order = Order(user_id=current_user.id, total_amount=total_amount, status='Pending')
    db.session.add(new_order)
    db.session.flush() # To get the order ID
    
    for oi in order_items:
        oi.order_id = new_order.id
        db.session.add(oi)
        
    db.session.commit()
    
    try:
        if stripe.api_key == 'sk_test_put_your_stripe_secret_key_here':
            # MOCK STRIPE FLOW
            new_order.stripe_payment_id = f'mock_session_{new_order.id}'
            db.session.commit()
            return jsonify({'url': url_for('payment_success', order_id=new_order.id, _external=True)})
        else:
            # REAL STRIPE FLOW
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=url_for('payment_success', order_id=new_order.id, _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=url_for('payment_cancel', order_id=new_order.id, _external=True),
            )
            new_order.stripe_payment_id = session.id
            db.session.commit()
            return jsonify({'url': session.url})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/payment/success/<int:order_id>')
@login_required
def payment_success(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status == 'Pending':
        order.status = 'Paid'
        # Deduct stock now that payment is confirmed
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock -= item.quantity
        db.session.commit()
    flash('Payment successful! Your order has been placed.', 'success')
    return redirect(url_for('orders'))

@app.route('/payment/cancel/<int:order_id>')
@login_required
def payment_cancel(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status == 'Pending':
        order.status = 'Cancelled'
        db.session.commit()
    flash('Payment was cancelled. You can try again.', 'danger')
    return redirect(url_for('checkout'))

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'image_url': product.image_url,
        'category': product.category
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
