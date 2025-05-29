from django.db import models

# Для главной страницы
class MainPage(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание профессии (2000+ символов)")
    image = models.ImageField(upload_to="main/", verbose_name="Изображение профессии")

    def __str__(self):
        return self.title

# Общий шаблон для таблиц и графиков по каждому разделу
class StatSection(models.Model):
    SECTION_CHOICES = [
        ('overview', 'Общая статистика'),
        ('demand', 'Востребованность'),
        ('geo', 'География'),
        ('skills', 'Навыки'),
    ]
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, verbose_name="Раздел")
    name = models.CharField(max_length=255, verbose_name="Название блока (например, Динамика зарплат)")
    html_table = models.TextField(verbose_name="HTML таблица")
    image = models.ImageField(upload_to="graphs/", verbose_name="График")

    def __str__(self):
        return f"{self.get_section_display()} — {self.name}"

class Vacancy(models.Model):
    name = models.CharField(max_length=255)
    salary_from= models.FloatField(null=True, blank=True)
    salary_to = models.FloatField(null=True, blank=True)
    salary_currency = models.CharField(max_length=10, null=True, blank=True)
    area_name = models.CharField(max_length=255, null=True, blank=True)
    published_at = models.DateField(null=True, blank=True)
    key_skills = models.TextField(null=True, blank=True)
    is_relevant = models.BooleanField(default=True)

    def __str__(self):
        return self.name

