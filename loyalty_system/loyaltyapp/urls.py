from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('shop/<int:shop_id>/', views.shop_items_view, name='shop_items'),
    path('purchase/<int:shop_id>/', views.purchase_view, name='purchase_view'),
]