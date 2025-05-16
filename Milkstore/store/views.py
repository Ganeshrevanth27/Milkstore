from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
import random

from .forms import RegisterForm
from .models import Product, Cart, Order, OrderItem, EmailOTP

# Utility to generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# OTP Registration Step 1: Send OTP
def register_request(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        email = request.POST.get('email')

        if form.is_valid():
            otp = generate_otp()
            EmailOTP.objects.update_or_create(email=email, defaults={'otp': otp})

            send_mail(
                subject='Your MilkStore Registration OTP',
                message=f'Your OTP is: {otp}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            request.session['registration_data'] = request.POST
            messages.success(request, 'OTP sent to your email. Please check your inbox.')
            return redirect('verify_otp')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

# OTP Registration Step 2: Verify and create user
def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp_input = request.POST.get('otp')

        try:
            otp_record = EmailOTP.objects.get(email=email)
        except EmailOTP.DoesNotExist:
            messages.error(request, 'No OTP found. Please register again.')
            return redirect('register')

        if otp_record.is_expired():
            otp_record.delete()
            messages.error(request, 'OTP expired. Please register again.')
            return redirect('register')

        if otp_record.otp != otp_input:
            messages.error(request, 'Invalid OTP. Try again.')
            return render(request, 'verify_otp.html', {'email': email})

        data = request.session.get('registration_data')
        if not data:
            messages.error(request, 'Session expired. Please register again.')
            return redirect('register')

        if User.objects.filter(username=data['username']).exists():
            messages.error(request, 'Username already taken.')
            return redirect('register')

        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password1']
        )
        user.is_active = True
        user.save()

        del request.session['registration_data']
        otp_record.delete()

        login(request, user)
        messages.success(request, 'Registration successful and logged in!')
        return redirect('home')

    email = request.session.get('registration_data', {}).get('email', '')
    return render(request, 'verify_otp.html', {'email': email})

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

# Home View
@login_required
def home_view(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

# Search View
def search_view(request):
    query = request.GET.get('q')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    return render(request, 'home.html', {'products': products})

# Product Detail
def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})

# Add to Cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    messages.success(request, "Product added to cart successfully!")
    return redirect('view_cart')

# View Cart
@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

# Buy Now
@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        address = request.POST.get("address", "")
        return redirect('checkout')
    return render(request, 'buy_now.html', {'product': product})

# Checkout View
@login_required
def checkout(request):
    if request.method == "POST":
        name = request.POST["name"]
        address = request.POST["address"]
        phone = request.POST["phone"]

        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect("view_cart")

        order = Order.objects.create(
            user=request.user,
            name=name,
            address=address,
            phone=phone,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
        cart_items.delete()
        messages.success(request, "Order placed successfully!")
        return redirect("order_history")

    return render(request, "store/checkout.html")

# Order History
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-ordered_at")
    return render(request, "order_history.html", {"orders": orders})