from django.contrib import admin
from .models import Market, Brande, Category, Product, Sklad, Ostatki_na_sklade, Review

admin.site.register([Market, Brande, Category, Product, Sklad, Ostatki_na_sklade, Review])
