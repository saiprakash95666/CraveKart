from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.views import View
from .models import Product, Customer, Cart
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
import stripe
from django.conf import settings
from .models import Payment, Order

stripe.api_key = settings.STRIPE_SECRET_KEY

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Create your views here.
def home(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
    return render(request, 'app/home.html', locals())

def about(request):
    totalitem = 0
    cart_count = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        cart_count = Cart.objects.filter(user=request.user).count()
    return render(request, 'app/about.html', locals())

def contact(request):
    totalitem = 0
    cart_count = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        cart_count = Cart.objects.filter(user=request.user).count()
    return render(request, 'app/contact.html', locals())

class CategoryView(View):
    def get(self, request, val):
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        product = Product.objects.filter(category=val)
        title = product.values('title').annotate(total=Count('title'))
        return render(request, 'app/category.html', locals())

class CategoryTitle(View):
    def get(self, request, val):
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request, 'app/category.html', locals())

class ProductDetail(View):
    def get(self, request, pid):
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        product = Product.objects.get(pk=pid)
        return render(request, 'app/productdetail.html', locals())

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', locals())

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Congratulations! User Registration Successful")
        else:
            messages.error(request, "Invalid Input Data")
        return render(request, 'app/customerregistration.html', locals())

class ProfileView(View):
    def get(self, request):
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', locals())

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user, name=name, locality=locality, mobile=mobile, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, "Congratulations! Profile saved successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return render(request, 'app/profile.html', locals())

def address(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
    cust_card = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', locals())

class EditAddress(View):
    def get(self, request, pk):
        cart_count = 0
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user=request.user).count()
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'app/editAddress.html', locals())

    def post(self, request, pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request, "Congratulations! Profile Update Successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return redirect('address')

def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')

def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    cart_count = 0
    if user.is_authenticated:
        cart_count = cart.count()
    for item in cart:
        value = item.quantity * item.product.price
        amount = round(amount + value, 2)
    totalamount = round(amount + 4, 2)
    return render(request, 'app/addtocart.html', locals())

class Checkout(View):
    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        tamount = 0
        cart_count = 0
        if user.is_authenticated:
            cart_count = cart_items.count()
        for i in cart_items:
            value = i.quantity * i.product.price
            tamount += value
        totalamount = round(tamount + 4, 2)
        return render(request, 'app/checkout.html', {
            'add': add,
            'cart_items': cart_items,
            'totalamount': totalamount,
            'cart_count': cart_count,
            'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        })

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user)).first()
        if c:
            c.quantity += 1
            c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = sum(p.quantity * p.product.price for p in cart)
        amount = round(amount, 2)
        totalamount = round(amount + 4, 2)
        data = {
            'quantity': c.quantity if c else 0,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user)).first()
        if c and c.quantity > 1:
            c.quantity -= 1
            c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = sum(p.quantity * p.product.price for p in cart)
        amount = round(amount, 2)
        totalamount = round(amount + 4, 2)
        data = {
            'quantity': c.quantity if c else 0,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        cart_items = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user))
        cart_items.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = sum(p.quantity * p.product.price for p in cart)
        amount = round(amount, 2)
        totalamount = round(amount + 4, 2)
        data = {
            'amount': amount,
            'totalamount': totalamount,
            'cart_empty': cart.count() == 0
        }
        return JsonResponse(data)

@method_decorator(csrf_exempt, name='dispatch')
class CreateStripeCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        customer_id = request.POST.get('custid')
        totalamount = float(request.POST.get('totamount'))

        customer = Customer.objects.get(id=customer_id)

        # Create Payment object first
        payment = Payment.objects.create(
            user=user,
            amount=totalamount,
        )

        # Create Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Order from Your Store',
                    },
                    'unit_amount': int(totalamount * 100),  # Stripe uses cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/payment-success/') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri('/payment-cancel/'),
            metadata={
                'payment_id': str(payment.id),
                'user_id': str(user.id),
                'customer_id': str(customer.id),
            }
        )

        payment.stripe_order_id = session.id
        payment.save()

        return JsonResponse({'sessionId': session.id})
    
class PaymentSuccessView(View):
    def get(self, request):
        session_id = request.GET.get('session_id')
        session = stripe.checkout.Session.retrieve(session_id)
        payment_id = session.metadata.get('payment_id')

        payment = Payment.objects.get(id=payment_id)
        payment.paid = True
        payment.stripe_payment_intent = session.payment_intent
        payment.save()

        # Create Order(s) for this Payment
        user = request.user
        customer = Customer.objects.get(id=session.metadata.get('customer_id'))
        cart_items = Cart.objects.filter(user=user)

        for item in cart_items:
            Order.objects.create(
                user=user,
                customer=customer,
                product=item.product,
                quantity=item.quantity,
                payment=payment
            )
            item.delete()  # clear cart after order

        messages.success(request, "Payment successful and Order placed!")
        return redirect('home')  # or show a nice success page


def payment_cancel(request):
    messages.warning(request, "Payment was cancelled.")
    return redirect('checkout')

def orders(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
    order_placed = Order.objects.filter(user=request.user)
    return render(request, 'app/orders.html', locals())

def search(request):
    query = request.GET['search']
    totalitem = 0
    cart_count = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        cart_count = Cart.objects.filter(user=request.user).count()
    items = Product.objects.filter(Q(title__icontains=query))
    return render(request,'app/search.html',locals())
