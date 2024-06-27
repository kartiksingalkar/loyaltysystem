from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Shop(models.Model):
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    merchant_id = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=100)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    loyalty_points = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    points_balance = models.IntegerField(default=0)
    active_points = models.IntegerField(default=0)
    expired_points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class LoyaltyPoint(models.Model):
    STATUS_CHOICES = [
        ('EARNED', 'Earned'),
        ('ACTIVE', 'Active'),
        ('REDEEMED', 'Redeemed'),
        ('EXPIRED', 'Expired'),
    ]

    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    points = models.IntegerField()
    date_earned = models.DateTimeField(auto_now_add=True)
    activation_date = models.DateTimeField()
    expiration_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='EARNED')
    redeemed_points = models.IntegerField(default=0)
    non_expiry = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.user.username} - {self.points} points"

class PointTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('EARN', 'Earn'),
        ('REDEEM', 'Redeem'),
    ]

    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    bill_no = models.CharField(max_length=50)
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    points_earned = models.IntegerField(default=0)
    points_redeemed = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()
    # merchant_id = models.ForeignKey(Shop, related_name='merchant_transactions', on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)

    def __str__(self):
        return f"{self.customer.user.username} - {self.transaction_type} - {self.points_earned if self.transaction_type == 'EARN' else self.points_redeemed} points"

class Redemption(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    points_used = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    details = models.TextField()
    points_detail = models.JSONField()

    def __str__(self):
        return f"{self.customer.user.username} - {self.points_used} points redeemed"


class Purchase(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, default=1)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField()
    total_points_earned = models.IntegerField(default=0)
    bill_no = models.CharField(max_length=50)
    points_redeemed = models.IntegerField(default=0)
    expiration_date = models.DateField()
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # merchant = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='merchant_transactions')

    def __str__(self):
        return f"{self.customer.user.username} - {self.total_points_earned} points earned"

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    points_earned = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.purchase.customer.user.username} - {self.item.name} - {self.quantity} - {self.points_earned} points"