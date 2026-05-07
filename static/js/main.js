// Cart State
let cart = JSON.parse(localStorage.getItem('ecommerce_cart')) || [];

// DOM Elements
const cartBtn = document.getElementById('cartBtn');
const closeCartBtn = document.getElementById('closeCart');
const cartOverlay = document.getElementById('cartOverlay');
const backdrop = document.getElementById('backdrop');
const cartItemsContainer = document.getElementById('cartItems');
const cartTotalElement = document.getElementById('cartTotal');
const cartCountElements = document.querySelectorAll('.cart-count');

// Toast Notification System
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    toast.innerHTML = `<i class="fas ${icon}"></i> <span>${message}</span>`;
    
    container.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove after 3s
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateCartUI();
    
    // Add to cart buttons
    const addToCartBtns = document.querySelectorAll('.add-to-cart-btn');
    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const product = {
                id: e.currentTarget.dataset.id,
                name: e.currentTarget.dataset.name,
                price: parseFloat(e.currentTarget.dataset.price),
                image: e.currentTarget.dataset.image
            };
            addToCart(product);
            showToast(`${product.name} added to cart!`, 'success');
            
            // Animation effect
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check"></i> Added';
            btn.style.background = '#22c55e';
            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.style.background = '';
            }, 2000);
        });
    });

    // Cart Toggle
    if (cartBtn) cartBtn.addEventListener('click', openCart);
    if (closeCartBtn) closeCartBtn.addEventListener('click', closeCart);
    if (backdrop) backdrop.addEventListener('click', closeCart);
    
    // Checkout Button
    const checkoutBtn = document.getElementById('checkoutBtn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', handleCheckout);
    }
    
    // Search Functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const products = document.querySelectorAll('.product-card');
            products.forEach(card => {
                const title = card.querySelector('.product-title').textContent.toLowerCase();
                // Since category is now section-based, search globally
                if (title.includes(query)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Wishlist Toggle
    const wishlistBtns = document.querySelectorAll('.wishlist-btn');
    wishlistBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault(); // prevent triggering outer links
            const icon = btn.querySelector('i');
            if (icon.classList.contains('far')) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                icon.style.color = '#ef4444';
                showToast('Added to Wishlist!', 'success');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                icon.style.color = 'inherit';
                showToast('Removed from Wishlist.', 'success');
            }
        });
    });

    // Banner Slider Logic
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    const nextBtn = document.querySelector('.next-btn');
    const prevBtn = document.querySelector('.prev-btn');
    const slidesContainer = document.querySelector('.banner-slides');
    
    if (slidesContainer) {
        let currentSlide = 0;
        const totalSlides = slides.length;
        let slideInterval;

        const updateSlider = () => {
            slidesContainer.style.transform = `translateX(-${currentSlide * 100}%)`;
            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === currentSlide);
            });
        };

        const nextSlide = () => {
            currentSlide = (currentSlide + 1) % totalSlides;
            updateSlider();
        };

        const prevSlide = () => {
            currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
            updateSlider();
        };

        nextBtn.addEventListener('click', () => { nextSlide(); resetInterval(); });
        prevBtn.addEventListener('click', () => { prevSlide(); resetInterval(); });

        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                currentSlide = index;
                updateSlider();
                resetInterval();
            });
        });

        const startInterval = () => {
            slideInterval = setInterval(nextSlide, 5000);
        };

        const resetInterval = () => {
            clearInterval(slideInterval);
            startInterval();
        };

        startInterval();
    }
});

function openCart() {
    cartOverlay.classList.add('open');
    backdrop.classList.add('show');
}

function closeCart() {
    cartOverlay.classList.remove('open');
    backdrop.classList.remove('show');
}

function addToCart(product) {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ ...product, quantity: 1 });
    }
    saveCart();
    updateCartUI();
    openCart();
}

function updateQuantity(id, change) {
    const item = cart.find(item => item.id === id);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            cart = cart.filter(item => item.id !== id);
        }
        saveCart();
        updateCartUI();
    }
}

function saveCart() {
    localStorage.setItem('ecommerce_cart', JSON.stringify(cart));
}

function updateCartUI() {
    // Update Counts
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCountElements.forEach(el => el.textContent = totalItems);
    
    // Update Items List
    if (!cartItemsContainer) return;
    
    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p style="text-align:center; color:var(--text-secondary); margin-top:2rem;">Your cart is empty.</p>';
        if (cartTotalElement) cartTotalElement.textContent = '₹0.00';
        return;
    }

    let total = 0;
    cartItemsContainer.innerHTML = cart.map(item => {
        total += item.price * item.quantity;
        return `
            <div class="cart-item">
                <img src="${item.image}" alt="${item.name}" class="cart-item-img">
                <div class="cart-item-info">
                    <div class="cart-item-title">${item.name}</div>
                    <div class="cart-item-price">₹${item.price.toFixed(2)}</div>
                    <div class="cart-qty-controls">
                        <button class="qty-btn" onclick="updateQuantity('${item.id}', -1)">-</button>
                        <span>${item.quantity}</span>
                        <button class="qty-btn" onclick="updateQuantity('${item.id}', 1)">+</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    if (cartTotalElement) {
        cartTotalElement.textContent = `₹${total.toFixed(2)}`;
    }
}

async function handleCheckout() {
    if (cart.length === 0) {
        showToast('Your cart is empty!', 'error');
        return;
    }

    // Check if user is logged in
    try {
        const btn = document.getElementById('checkoutBtn');
        btn.innerHTML = '<div class="spinner"></div> Processing...';
        btn.disabled = true;

        const response = await fetch('/api/create-checkout-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ cart })
        });

        const data = await response.json();

        if (response.ok) {
            cart = [];
            saveCart();
            window.location.href = data.url;
        } else if (response.status === 401) {
            // Not logged in
            window.location.href = '/login?next=/checkout';
        } else {
            showToast(data.error || 'An error occurred during checkout.', 'error');
            btn.innerHTML = 'Proceed to Checkout';
            btn.disabled = false;
        }
    } catch (error) {
        console.error('Checkout error:', error);
        showToast('Failed to connect to the server.', 'error');
        const btn = document.getElementById('checkoutBtn');
        btn.innerHTML = 'Proceed to Checkout';
        btn.disabled = false;
    }
}
