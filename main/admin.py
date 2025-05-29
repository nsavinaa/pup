from django.contrib import admin
from .models import MainPage, StatSection

@admin.register(MainPage)
class MainPageAdmin(admin.ModelAdmin):
    list_display = ("title",)

@admin.register(StatSection)
class StatSectionAdmin(admin.ModelAdmin):
    list_display = ("section", "name")
    list_filter = ("section",)
