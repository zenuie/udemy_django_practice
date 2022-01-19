from django.contrib import admin
from .models import Category


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    # 可以跟隨category_name去做相對應名稱
    prepopulated_fields = {'slug': ('category_name',)}

    # 列表篩選
    list_display = ('category_name', 'slug')


admin.site.register(Category, CategoryAdmin)
