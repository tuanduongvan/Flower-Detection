from django.contrib import admin
from .models import Flower, SearchHistory

# Register your models here.
admin.site.register(Flower)
admin.site.register(SearchHistory)