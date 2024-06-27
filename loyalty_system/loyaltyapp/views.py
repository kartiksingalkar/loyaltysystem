from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Shop, Item, CustomerProfile, Purchase, PurchaseItem, LoyaltyPoint, PointTransaction
from django.utils import timezone
from datetime import timedelta

# Create your views here.


def home(request):
    shops = Shop.objects.all()
    return render(request, 'loyalty/base.html', {'shops': shops})

def shop_items_view(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    items = Item.objects.filter(shop=shop)
    return render(request, 'loyalty/shop_items.html', {'shop': shop, 'items': items})


def purchase_view(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    customer = request.user.customerprofile

    if request.method == 'POST':
        item_id = request.POST['item_id']
        quantity = int(request.POST['quantity'])
        redeem_points = int(request.POST['redeem_points'])
        expiration_date = request.POST['expiration_date']
        # merchant_id = request.POST['merchant_id']
        item = get_object_or_404(Item, id=item_id)
        total_price = item.price * quantity
        total_points_earned = item.loyalty_points * quantity

        # Check and apply redeemable points
        if redeem_points > customer.active_points:
            redeem_points = customer.active_points
        customer.active_points -= redeem_points
        customer.points_balance -= redeem_points

        bill_amount = total_price - redeem_points

        # Create purchase record
        purchase = Purchase.objects.create(
            customer=customer,
            shop=shop,
            item=item,
            quantity=quantity,
            total_price=total_price - redeem_points,
            total_points_earned=total_points_earned,
            date=timezone.now(),
            bill_no='BILL123',
            bill_amount=total_price,
            
            
        )

        # Update customer points
        customer.points_balance += total_points_earned
        customer.active_points += total_points_earned
        customer.save()

        # Log point transaction
        PointTransaction.objects.create(
            customer=customer,
            shop=shop,
            bill_no=purchase.bill_no,
            # items_received=f"{quantity} x {item.name}",
            points_earned=total_points_earned,
            points_redeemed=redeem_points,
            date=timezone.now(),
            expiration_date=expiration_date,
            # merchant_id=merchant_id,
            transaction_type='Purchase'
        )

        # Create LoyaltyPoint entry
        LoyaltyPoint.objects.create(
            customer=customer,
            shop=shop,
            points=total_points_earned,
            date_earned=timezone.now(),
            activation_date=timezone.now(),
            expiration_date=expiration_date,
            status='active'
        )

        return redirect('/')

    items = Item.objects.filter(shop=shop)
    loyalty_points = LoyaltyPoint.objects.filter(customer=customer, status='active')
    return render(request, 'loyalty/purchase.html', {'shop': shop, 'items': items, 'customer': customer, 'loyalty_points': loyalty_points})



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('/')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'loyalty/login.html', {'form': form})


