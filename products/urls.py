from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (MarketListCreateView, MarketDetailView,BrandeListCreateView, CategoryListCreateView,ProductListCreateView, ProductDetailView,SkladViewSet, OstatkiViewSet, ReviewViewSet)

router = DefaultRouter()
router.register('sklady', SkladViewSet)
router.register('ostatki', OstatkiViewSet)
router.register('reviews', ReviewViewSet)

urlpatterns = [
    path('markets/', MarketListCreateView.as_view()),
    path('markets/<int:pk>/', MarketDetailView.as_view()),
    path('brands/', BrandeListCreateView.as_view()),
    path('categories/', CategoryListCreateView.as_view()),
    path('products/', ProductListCreateView.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),
] + router.urls
