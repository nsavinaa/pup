from django.contrib import admin
from django.utils.html import format_html
from .models import MainPage, StatSection

@admin.register(MainPage)
class MainPageAdmin(admin.ModelAdmin):
    list_display = ("title",)


@admin.register(StatSection)
class StatSectionAdmin(admin.ModelAdmin):
    list_display = ("section", "name", "preview_image", "short_table")
    list_filter = ("section",)
    search_fields = ("name",)
    readonly_fields = ("preview_image", "short_table")
    fields = ("section", "name", "image", "preview_image", "html_table", "short_table")

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" />', obj.image.url)
        return "-"
    preview_image.short_description = "Превью графика"

    def short_table(self, obj):
        if obj.html_table:
            return format_html('<div style="max-height: 200px; overflow: auto;">{}</div>', obj.html_table)
        return "-"
    short_table.short_description = "HTML таблица"