from app import app, db, bcrypt
from models import User, Product

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Create Admin
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(username='admin', email='admin@ecommerce.com', password=hashed_pw, role='admin')
        
        # Create User
        hashed_pw2 = bcrypt.generate_password_hash('user123').decode('utf-8')
        user = User(username='testuser', email='user@ecommerce.com', password=hashed_pw2, role='user')

        db.session.add(admin)
        db.session.add(user)

        # Products (Flipkart Inspired, INR)
        products = [
            # Mobiles
            Product(
                name="SAMSUNG Galaxy S24 Ultra 5G (Titanium Gray, 256 GB)",
                description="Meet the Galaxy S24 Ultra, the ultimate smartphone with Galaxy AI. Titanium exterior, 200MP camera, and built-in S Pen.",
                price=129999.00,
                stock=45,
                image_url="https://images.unsplash.com/photo-1706132448354-9ee7ee872b2a?auto=format&fit=crop&w=1000&q=80",
                category="Mobiles"
            ),
            Product(
                name="Apple iPhone 15 (Blue, 128 GB)",
                description="Dynamic Island bubbles up alerts. 48MP Main camera. USB-C. All-day battery life.",
                price=72999.00,
                stock=120,
                image_url="https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=1000&q=80",
                category="Mobiles"
            ),
            Product(
                name="Motorola Edge 50 Pro 5G",
                description="World's 1st AI Powered Pro-Grade Camera. 144Hz 3D Curved Display, 125W TurboPower charging.",
                price=31999.00,
                stock=80,
                image_url="https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=1000&q=80",
                category="Mobiles"
            ),
            
            # Electronics (Laptops, Audio, Smartwatches)
            Product(
                name="Apple MacBook Air M3 (8GB/256GB SSD)",
                description="Supercharged by M3. 13.6-inch Liquid Retina display, up to 18 hours battery life.",
                price=114900.00,
                stock=25,
                image_url="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1000&q=80",
                category="Electronics"
            ),
            Product(
                name="Sony WH-1000XM5 Bluetooth Headphones",
                description="Industry leading noise cancellation, 30 hours battery life, multipoint connection.",
                price=29990.00,
                stock=150,
                image_url="https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=1000&q=80",
                category="Electronics"
            ),
            Product(
                name="ASUS TUF Gaming F15 (Intel Core i5 11th Gen, RTX 2050)",
                description="144Hz refresh rate, 8GB RAM, 512GB NVMe SSD, Windows 11 Home.",
                price=49990.00,
                stock=60,
                image_url="https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=1000&q=80",
                category="Electronics"
            ),
            Product(
                name="Noise ColorFit Pro 4 Alpha Smartwatch",
                description="1.78 inch AMOLED display, Bluetooth calling, functional crown.",
                price=2499.00,
                stock=300,
                image_url="https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=1000&q=80",
                category="Electronics"
            ),

            # Fashion
            Product(
                name="Puma Men's Graphic Printed T-Shirt",
                description="100% cotton, regular fit casual graphic print tee. Perfect for summer.",
                price=699.00,
                stock=200,
                image_url="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=1000&q=80",
                category="Fashion"
            ),
            Product(
                name="Nike Air Max 270 Sneakers",
                description="Nike's first lifestyle Air Max brings you style, comfort, and big attitude.",
                price=11895.00,
                stock=40,
                image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=1000&q=80",
                category="Fashion"
            ),
            Product(
                name="Levis Men Slim Fit Jeans",
                description="Stretchable slim fit jeans, premium denim fabric, classic 5-pocket styling.",
                price=1899.00,
                stock=120,
                image_url="https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=1000&q=80",
                category="Fashion"
            ),

            # Home & Furniture
            Product(
                name="Wakefit Orthopedic Memory Foam Mattress",
                description="King Size mattress with pressure relieving memory foam and breathable fabric.",
                price=12499.00,
                stock=35,
                image_url="https://images.unsplash.com/photo-1505693314120-0d443867891c?auto=format&fit=crop&w=1000&q=80",
                category="Home & Furniture"
            ),
            Product(
                name="Philips Hue White and Color Ambiance Smart Bulb",
                description="16 million colors, works with Alexa, Google Assistant, and Apple HomeKit.",
                price=2899.00,
                stock=80,
                image_url="https://images.unsplash.com/photo-1550989460-0adf9ea622e2?auto=format&fit=crop&w=1000&q=80",
                category="Home & Furniture"
            ),

            # Appliances
            Product(
                name="LG 8 Kg 5 Star Fully Automatic Front Load Washing Machine",
                description="AI DD Technology, Inverter Direct Drive, built-in heater, hygiene wash.",
                price=34990.00,
                stock=15,
                image_url="https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?auto=format&fit=crop&w=1000&q=80",
                category="Appliances"
            ),
            Product(
                name="Samsung 236 L 3 Star Frost Free Double Door Refrigerator",
                description="Digital Inverter Compressor, easily slide shelf, all-around cooling.",
                price=24490.00,
                stock=20,
                image_url="https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?auto=format&fit=crop&w=1000&q=80",
                category="Appliances"
            )
        ]

        for p in products:
            db.session.add(p)

        db.session.commit()
        print("Database seeded successfully with Flipkart-inspired INR products!")

if __name__ == '__main__':
    seed_data()
