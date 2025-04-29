from django.contrib import admin
from . models import Product, Customer, Cart, Payment, Order

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price', 'category', 'product_img']

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'locality', 'city', 'state', 'zipcode']

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity']

@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'stripe_order_id','stripe_payment_intent','paid']

@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customer', 'product','quantity','ordered_data','status','payment']