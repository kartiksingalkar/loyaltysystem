from django.contrib import admin
from .models import Shop, Item, CustomerProfile, LoyaltyPoint, PointTransaction, Redemption, Purchase, PurchaseItem

# Register your models here.

admin.site.register(Shop)
admin.site.register(Item)
admin.site.register(CustomerProfile)
admin.site.register(LoyaltyPoint)
admin.site.register(PointTransaction)
admin.site.register(Redemption)
admin.site.register(Purchase)
admin.site.register(PurchaseItem)