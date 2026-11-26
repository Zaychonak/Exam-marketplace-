from rest_framework import serializers
from .models import Karzina, Zakaz, SostavZakaza, Oplata, Vozvrat


class KarzinaSerializer(serializers.ModelSerializer):
    product_title = serializers.ReadOnlyField(source='product.title')
    product_price = serializers.ReadOnlyField(source='product.price')
    subtotal = serializers.SerializerMethodField()


    class Meta:
        model = Karzina
        fields = ('id', 'product', 'product_title', 'product_price', 'quantity', 'subtotal')

    def get_subtotal(self, obj):
        return obj.product.price * obj.quantity


class SostavZakazaSerializer(serializers.ModelSerializer):
    product_title = serializers.ReadOnlyField(source='product.title')

    class Meta:
        model = SostavZakaza
        fields = ('id', 'product', 'product_title', 'quantity', 'price')


class OplataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oplata
        fields = ('id', 'zakaz', 'amount', 'status', 'method', 'created_at')
        read_only_fields = ('id', 'amount', 'status', 'created_at')


class ZakazSerializer(serializers.ModelSerializer):
    items = SostavZakazaSerializer(many=True, read_only=True)
    payment = OplataSerializer(source='oplata_zakaz', read_only=True)

    class Meta:
        model = Zakaz
        fields = ('id', 'user', 'total_price', 'status', 'created_at', 'items', 'payment')
        read_only_fields = ('id', 'user', 'total_price', 'status', 'created_at')


class VozvratSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vozvrat
        fields = ('id', 'sostav_zakaza', 'reason', 'status', 'created_at')
        read_only_fields = ('id', 'status', 'created_at')