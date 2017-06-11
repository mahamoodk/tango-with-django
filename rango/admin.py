
from django.contrib import admin
from . models import Category, Page
from .models import UserProfile

#@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
    list_display = ('name', 'slug','views', 'likes')
admin.site.register(Category, CategoryAdmin)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url','views',)

admin.site.register(UserProfile)
