import os
import django
import pandas as pd
from tqdm import tqdm  # Установи через: pip install tqdm

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "profession_site.settings")
django.setup()

from main.models import Vacancy

# Удаление старых записей — если нужно
Vacancy.objects.all().delete()

# Импорт CSV с разбиением на части
filename = 'data/vacancies_2024.csv'
chunksize = 1000

# Вычисляем общее количество строк
with open(filename, encoding='utf-8') as f:
    total_rows = sum(1 for _ in f) - 1  # без заголовка

# Чтение по кусочкам с прогресс-баром
for chunk in tqdm(pd.read_csv(filename, encoding='utf-8', chunksize=chunksize, low_memory=False),
                  total=total_rows // chunksize + 1):
    vacancies = []
    for _, row in chunk.iterrows():
        try:
            vacancy = Vacancy(
                name=row.get('name'),
                salary_from=float(row['salary_from']) if pd.notnull(row['salary_from']) else None,
                salary_to=float(row['salary_to']) if pd.notnull(row['salary_to']) else None,
                salary_currency=row.get('salary_currency'),
                area_name=row.get('area_name'),
                published_at=row['published_at'][:10] if pd.notnull(row.get('published_at')) else None,
                key_skills=row.get('key_skills'),
            )
            vacancies.append(vacancy)
        except Exception as e:
            print(f"[Ошибка] Строка пропущена: {e}")

    # Массовая вставка
    Vacancy.objects.bulk_create(vacancies)

