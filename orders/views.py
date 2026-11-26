from django.core.cache import cache
from django.db import transaction
from django.db.models import F
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Ostatki_na_sklade
from .models import Karzina, Zakaz, SostavZakaza, Oplata, Vozvrat
from .serializer import (KarzinaSerializer, ZakazSerializer,OplataSerializer, VozvratSerializer)
from .task import send_order_confirmation_email, cancel_unpaid_order


class KarzinaListCreateView(generics.ListCreateAPIView):
    serializer_class = KarzinaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Karzina.objects.filter(user=self.request.user).select_related('product')

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        quantity = serializer.validated_data.get('quantity', 1)

        item, created = Karzina.objects.get_or_create(user=self.request.user, product=product, defaults={'quantity': quantity})
        if not created:
            item.quantity += quantity
            item.save()


class KarzinaDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = KarzinaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Karzina.objects.filter(user=self.request.user)

    
class CheckoutView(generics.CreateAPIView):
    serializer_class = ZakazSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart_items = Karzina.objects.filter(user=request.user)
        if not cart_items:
            return Response({"error": "Корзина пуста!"}, status=400)

        total_price = 0
        for pro in cart_items:
            ostatok = Ostatki_na_sklade.objects.filter(product=pro.product).first()

            if not ostatok or ostatok.quantity < pro.quantity:
                return Response({'error': f'Its dont enought{pro.product.title}'},status=400)
            
            total_price += item.product.price * item.quantity

        zakaz = Zakaz.objects.create(user=request.user, total_price=total_price)

        for item in cart_items:
            SostavZakaza.objects.create(
                zakaz=zakaz,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            ostatok = Ostatki_na_sklade.objects.filter(product=item.product).first()
            ostatok.quantity -= item.quantity
            ostatok.save()

#ija redisay
        cart_items.delete()
        cache.clear()

#ija celerya
        send_order_confirmation_email.delay(zakaz.id)

        serializer = self.get_serializer(zakaz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class ZakazListView(generics.ListAPIView):
    serializer_class = ZakazSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Zakaz.objects.filter(user=self.request.user).prefetch_related('items__product').select_related('oplata_zakaz').order_by('-created_at'))


class OplataCreateView(generics.CreateAPIView):
    serializer_class = OplataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        zakaz = serializer.validated_data['zakaz']
        serializer.save(user=self.request.user, amount=zakaz.total_price, status='success')
        zakaz.status = 'paid'
        zakaz.save()


class VozvratListCreateView(generics.ListCreateAPIView):
    serializer_class = VozvratSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vozvrat.objects.filter(sostav_zakaza__zakaz__user=self.request.user)
