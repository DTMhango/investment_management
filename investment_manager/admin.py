from django.contrib import admin
from .models import Client, Investment, Contribution

admin.site.register((Client, Investment, Contribution))
