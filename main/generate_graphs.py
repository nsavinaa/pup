import os
import django
import matplotlib.pyplot as plt
from collections import Counter

# Настройка Django окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'profession_site.settings')  # замени на имя своего проекта
django.setup()

from main.models import Vacancy

# Подготовка директории
os.makedirs('media/graphs', exist_ok=True)

# Счётчик навыков
skills_counter = Counter()

# Собираем все навыки
for vacancy in Vacancy.objects.exclude(key_skills=None):
    skills = vacancy.key_skills.split('\n')  # skills в одной строке с \n
    skills_counter.update(skills)

# Получаем топ-20
top_skills = skills_counter.most_common(20)
skills, counts = zip(*top_skills)

# Строим график
plt.figure(figsize=(12, 6))
plt.barh(skills[::-1], counts[::-1], color="#3498db")
plt.xlabel("Количество упоминаний")
plt.title("Топ-20 навыков в вакансиях")

# Сохраняем
plt.tight_layout()
plt.savefig('media/graphs/skills.png')
plt.close()

print("График сохранён в media/graphs/skills.png")