from rest_framework import serializers
from .models import (Market, Brande, Category, Product, Sklad, Ostatki_na_sklade, Review)

class MarketSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source = 'user.username')
    products_count = serializers.IntegerField(read_only=True)


    class Meta:
        model = Market
        fields = ['id', 'user', 'title', 'description', 'products_count']


class BrandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brande
        fields = ('id', 'title', 'description')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')


class SkladSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sklad
        fields = ('id', 'city', 'address')


class OstatkiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ostatki_na_sklade
        fields = ('id', 'product', 'sklad', 'quantity')


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:

        model = Review
        fields = ('id', 'product', 'user', 'stars', 'comment', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')


class ProductSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(source='reviews_product', many=True, read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    total_stock = serializers.IntegerField(read_only=True)
    market_title = serializers.ReadOnlyField(source='market.title')
    category_name = serializers.ReadOnlyField(source='category.name')
    brande_title = serializers.ReadOnlyField(source='brande.title')

    class Meta:
        model = Product
        fields = ('id', 'market', 'market_title', 'brande', 'brande_title','category', 'category_name', 'title', 
                'description','price', 'article', 'color', 'size', 'photo','reviews', 'avg_rating', 'total_stock')

    def validate_market(self, market):
        request = self.context.get('request')
        if request and market.user != request.user:
            raise serializers.ValidationError("Youu can add product only in your market (shop)!!!")
        return market
