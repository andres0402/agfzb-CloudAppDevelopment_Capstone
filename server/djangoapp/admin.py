from django.contrib import admin
from .models import CarMake, CarModel

# Define the CarModelInline class
class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 1 

# Define the CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'dealer_id', 'model_type', 'year']
    list_filter = ['name', 'year']
    search_fields = ['name', 'make__name']
    list_per_page = 20

# Register CarModelAdmin as the admin for CarModel
admin.site.register(CarModel, CarModelAdmin)

# Define the CarMakeAdmin class with CarModelInline
@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = ['name', 'description']
    search_fields = ['name']
    list_per_page = 20
