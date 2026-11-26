from django.shortcuts import render
from .models import (Market, Brande, Category, Product, Sklad, Ostatki_na_sklade, Review)
from django.core.cache import cache
from rest_framework import viewsets, permissions, generics, filters
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from .serializer import (MarketSerializer, BrandeSerializer, CategorySerializer,ProductSerializer, SkladSerializer, OstatkiSerializer, ReviewSerializer)
from .permissions import IsOwnerReadOnly
from django.db.models import Avg, Sum, Count, Prefetch, Value, FloatField, IntegerField
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


PRODUCTS_CACHE_KEY = 'products_catalog_v1'


class MarketListCreateView(generics.ListCreateAPIView):
    queryset = Market.objects.select_related('user').annotate(products_count = Count('product_market'))
    serializer_class = MarketSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)


class MarketDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Market.objects.select_related('user').annotate(products_count = Count('product_market'))
    serializer_class = MarketSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerReadOnly]


class BrandeListCreateView(generics.ListCreateAPIView):
    queryset = Brande.objects.all()
    serializer_class = BrandeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser] 
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'article', 'description', 'category__name', 'brande__title']

    def get_queryset(self):
        queryset = (Product.objects.select_related('market', 'brande', 'category')
                         .prefetch_related('reviews_product__user').annotate(avg_rating = Avg('reviews_product__stars'),
                                                                            total_stock=Sum('stocks_product__quantity'),).order_by('-id'))


        category_id = self.request.query_params.get('category')
        brande_id = self.request.query_params.get('brande')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if brande_id:
            queryset = queryset.filter(brande_id=brande_id)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

    
    def list(self, request, *args, **kwargs):
        cached_data = cache.get('products_list')
        if cached_data is not None:
            print('redis poshol vzyat dannie ot db')
            return Response(cached_data)

        print("vzyal")
        response = super().list(request, *args, **kwargs)
        cache.set('products_list', response.data, timeout=300)
        return response

    def perform_create(self, serializer):
        serializer.save()
        cache.clear()
        print('ochisteli redis')


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerReadOnly]

    def get_queryset(self):
        return (
            Product.objects
            .select_related('market', 'brande', 'category')
            .prefetch_related('reviews_product__user')
            .annotate(
                avg_rating=Avg('reviews_product__stars'),
                total_stock=Sum('stocks_product__quantity'),
            )
        )

    def perform_update(self, serializer):
        serializer.save()
        cache.clear()

    def perform_destroy(self, instance):
        instance.delete()
        cache.clear()




class SkladViewSet(viewsets.ModelViewSet):
    queryset = Sklad.objects.all()
    serializer_class = SkladSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class OstatkiViewSet(viewsets.ModelViewSet):
    queryset = Ostatki_na_sklade.objects.select_related('product', 'sklad')
    serializer_class = OstatkiSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()
        cache.clear()

    def perform_update(self, serializer):
        serializer.save()
        cache.clear()



class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'product')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        cache.clear()