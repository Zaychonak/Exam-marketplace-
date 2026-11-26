from django.urls import path
from .views import (
    KarzinaListCreateView, KarzinaDetailView,
    CheckoutView, ZakazListView,
    OplataCreateView, VozvratListCreateView
)

urlpatterns = [
    path('cart/', KarzinaListCreateView.as_view(), name='cart-list'),
    path('cart/<int:pk>/', KarzinaDetailView.as_view(), name='cart-detail'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('my-orders/', ZakazListView.as_view(), name='order-list'),
    path('pay/', OplataCreateView.as_view(), name='order-pay'),
    path('returns/', VozvratListCreateView.as_view(), name='order-returns'),
]
