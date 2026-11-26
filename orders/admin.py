from django.contrib import admin
from .models import Karzina, Zakaz, SostavZakaza, Oplata, Vozvrat

admin.site.register([Karzina, Zakaz, SostavZakaza, Oplata, Vozvrat])
