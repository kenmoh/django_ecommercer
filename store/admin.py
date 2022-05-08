from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from .models import Collection, Product, Customer, Order

product_is_low = 'low_inventory'


class FilterInventory(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            (product_is_low, 'Low')
        ]

    def queryset(self, request, queryset):
        if self.value() == product_is_low:
            return queryset.filter(inventory__lt=20)


# noinspection PyMethodMayBeStatic
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit_price', 'inventory_status']
    list_editable = ['unit_price']
    list_per_page = 50
    list_filter = ['collection', 'last_update', FilterInventory]

    # Computed Field
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 20:
            return 'Low'
        return 'OK'


# noinspection PyMethodMayBeStatic
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders']
    list_editable = ['membership']
    ordering = ['first_name', 'last_name']
    list_per_page = 50
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='orders')
    def orders(self, customer):
        return customer.order_set.count()

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders=Count('order')
        )


# noinspection PyMethodMayBeStatic
@admin.register(Collection)
class CollectionAdin(admin.ModelAdmin):
    list_display = ['title', 'product_count']

    # Computed Field
    @admin.display(ordering='product_count')
    def product_count(self, collection):
        url = (reverse('admin:store_product_changelist')
               + '?'
               + urlencode({
                    'collection__id': str(collection.id)
                }))
        return format_html(f'<a href={url}>{collection.product_count}</a>')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=Count('product')
        )


admin.site.register(Order)
