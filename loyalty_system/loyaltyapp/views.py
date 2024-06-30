from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Shop, Item, CustomerProfile, Purchase, LoyaltyPoint, PointTransaction
from django.utils import timezone
import secrets
import string
from django.utils.dateparse import parse_date
from datetime import datetime, date

# Create your views here.


def home(request):
    shops = Shop.objects.all()
    return render(request, 'loyalty/base.html', {'shops': shops})

def shop_items_view(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    items = Item.objects.filter(shop=shop)
    return render(request, 'loyalty/shop_items.html', {'shop': shop, 'items': items})

def generate_bill_no(length=5):
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))

bill_no = generate_bill_no()

def calculate_status(activation_date, expiration_date):
    now = timezone.now().date()
    if now < activation_date:
        return 'pending'
    elif now > expiration_date:
        return 'expired'
    else:
        return 'active'
    
def redeem_loyalty_points(customer, points_to_redeem):
    # Get active loyalty points sorted by expiration date
    active_points = LoyaltyPoint.objects.filter(customer=customer, status='active').order_by('expiration_date')
    redeemed_points_detail = []

    remaining_points_to_redeem = points_to_redeem

    for point in active_points:
        if remaining_points_to_redeem <= 0:
            break

        points_available = point.points - point.redeemed_points

        if points_available > 0:
            if points_available >= remaining_points_to_redeem:
                point.redeemed_points += remaining_points_to_redeem
                redeemed_points_detail.append({
                    'point_id': point.id,
                    'points_redeemed': remaining_points_to_redeem
                })
                remaining_points_to_redeem = 0
            else:
                point.redeemed_points += points_available
                redeemed_points_detail.append({
                    'point_id': point.id,
                    'points_redeemed': points_available
                })
                remaining_points_to_redeem -= points_available

            # Change status to 'redeemed' if fully redeemed
            if point.redeemed_points >= point.points:
                point.status = 'redeemed'
            point.save()

    return redeemed_points_detail

def purchase_view(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    customer = request.user.customerprofile

    if request.method == 'POST':
        item_id = request.POST['item_id']
        quantity = int(request.POST['quantity'])
        redeem_points = int(request.POST['redeem_points'])
        activation_date_str = request.POST['activation_date']
        expiration_date_str = request.POST['expiration_date']
        
        # Convert string dates to datetime.date objects
        activation_date = parse_date(activation_date_str)
        expiration_date = parse_date(expiration_date_str)

        item = get_object_or_404(Item, id=item_id)
        total_price = item.price * quantity
        total_points_earned = item.loyalty_points * quantity

        # Redeem points
        redeemed_points_detail = redeem_loyalty_points(customer, redeem_points)
        total_redeemed_points = sum(detail['points_redeemed'] for detail in redeemed_points_detail)

        bill_amount = total_price - total_redeemed_points

        # Create purchase record
        purchase = Purchase.objects.create(
            customer=customer,
            shop=shop,
            item=item,
            quantity=quantity,
            total_price=total_price,
            total_points_earned=total_points_earned,
            date=timezone.now(),
            bill_no=generate_bill_no(),
            bill_amount=bill_amount,
            expiration_date=expiration_date,
            points_redeemed=total_redeemed_points,
        )

        # Update customer points
        customer.points_balance += total_points_earned - total_redeemed_points
        customer.active_points += total_points_earned - total_redeemed_points
        customer.save()

        # Log point transaction
        PointTransaction.objects.create(
            customer=customer,
            shop=shop,
            bill_no=purchase.bill_no,
            points_earned=total_points_earned,
            points_redeemed=total_redeemed_points,
            date=timezone.now(),
            expiration_date=expiration_date,
            transaction_type='Purchase'
        )

        status = calculate_status(activation_date, expiration_date)

        # Create LoyaltyPoint entry
        LoyaltyPoint.objects.create(
            customer=customer,
            shop=shop,
            points=total_points_earned,
            date_earned=timezone.now(),
            activation_date=activation_date,
            expiration_date=expiration_date,
            status=status
        )

        return redirect('/')

    items = Item.objects.filter(shop=shop)

    # Update statuses before fetching active points
    for point in LoyaltyPoint.objects.filter(customer=customer):
        point.status = calculate_status(point.activation_date.date(), point.expiration_date.date())
        point.save()

    loyalty_points = LoyaltyPoint.objects.filter(customer=customer, status='active')

    # Calculate total redeemable points
    total_redeemable_points = sum(point.points - point.redeemed_points for point in loyalty_points)

    return render(request, 'loyalty/purchase.html', {
        'shop': shop,
        'items': items,
        'customer': customer,
        'loyalty_points': loyalty_points,
        'total_redeemable_points': total_redeemable_points,
    })

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


