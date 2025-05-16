from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_request, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('search/', views.search_view, name='search'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('orders/', views.order_history, name='order_history'),
]
