import os
import matplotlib.pyplot as plt
from collections import Counter
from django.conf import settings
from .models import Vacancy
import math
from functools import reduce
from django.db.models import Q
from collections import defaultdict
from datetime import datetime
import statistics

currency_to_rub = {
    'RUR': 1,
    'USD': 80,
    'EUR': 90,
    'KZT': 0.15,
    'UZS': 0.006,
    'UAH': 1.9,
    'AZN': 45,
    'BYR': 31,
    'GEL': 29,
    'KGS': 0.9,
}
profession_keywords = ['аналитик', 'data analyst', 'аналитика', 'data analysis']
#общая статистика
def filter_vacancy_by_profession(vacancy_name, profession_keywords):
    """Проверяет, содержит ли название вакансии любое из ключевых слов профессии."""
    if not vacancy_name:
        return False
    vacancy_name_lower = vacancy_name.lower()
    for keyword in profession_keywords:
        if keyword.lower() in vacancy_name_lower:
            return True
    return False

def generate_vacancy_dynamics_chart():
    years = []

    for vacancy in Vacancy.objects.all():
        published_at = vacancy.published_at
        name = vacancy.name  #для восстребованности

        if not published_at or published_at == '':
            # Пропускаем None, пустые строки и похожие
            continue
        if profession_keywords:
            if not filter_vacancy_by_profession(name, profession_keywords):
                continue  # Пропускаем, если профессия не совпала, для восстребованности

        # Если это строка, пытаемся распарсить
        if isinstance(published_at, str):
            try:
                date_obj = datetime.strptime(published_at[:10], '%Y-%m-%d')
                years.append(date_obj.year)
            except Exception:
                continue
        else:
            try:
                years.append(published_at.year)
            except Exception:
                continue

    if not years:
        return

    year_counts = Counter(years)
    sorted_years = sorted(year_counts.keys())
    counts = [year_counts[year] for year in sorted_years]
    plt.figure(figsize=(10, 6))
    plt.plot(sorted_years, counts, marker='o', linestyle='-', color='royalblue')
    title = 'Динамика количества вакансий по годам'
    if profession_keywords:
        title += f' — профессия: {profession_keywords[0].capitalize()}'
    plt.title(title) #для аналитика
    #plt.title('Динамика количества вакансий по годам')
    plt.xlabel('Год')
    plt.ylabel('Количество вакансий')
    plt.grid(True)
    plt.tight_layout()

    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    filename = 'stat_vacancy_analyst_dynamics.png'
    path = os.path.join(graph_dir, filename) #аналитик
    #path = os.path.join(graph_dir, 'stat_vacancy_dynamics.png')
    plt.savefig(path)
    plt.close()

def generate_salary_dynamics_chart():
    from collections import defaultdict
    salaries_by_year = defaultdict(list)

    for vacancy in Vacancy.objects.exclude(published_at__isnull=True):
        try:
            year = vacancy.published_at.year
        except Exception:
            continue

        salary_from = vacancy.salary_from
        salary_to = vacancy.salary_to
        currency = vacancy.salary_currency

        if not currency or currency not in currency_to_rub:
            continue

        if salary_from and salary_to:
            salary = (salary_from + salary_to) / 2
        elif salary_from:
            salary = salary_from
        elif salary_to:
            salary = salary_to
        else:
            continue

        salary_rub = salary * currency_to_rub[currency]
        salaries_by_year[year].append(salary_rub)

    years = sorted(salaries_by_year.keys())
    if not years:
        return

    avg_salaries = [round(statistics.mean(salaries_by_year[year])) for year in years]

    plt.figure(figsize=(10, 6))
    plt.plot(years, avg_salaries, marker='o', color='teal')
    plt.title('Динамика уровня зарплат по годам (все вакансии)')
    plt.xlabel('Год')
    plt.ylabel('Средняя зарплата, руб.')
    plt.grid(True)
    plt.tight_layout()

    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    plt.savefig(os.path.join(graph_dir, 'salary_dynamics.png'))
    plt.close()

def generate_salary_analyst_dynamics_chart(profession_keywords):
    from collections import defaultdict
    salaries_by_year = defaultdict(list)

    vacancies = Vacancy.objects.filter(
        reduce(lambda q, keyword: q | Q(name__icontains=keyword), profession_keywords, Q())
    ).exclude(published_at__isnull=True)

    for vacancy in vacancies:
        try:
            year = vacancy.published_at.year
        except Exception:
            continue

        salary_from = vacancy.salary_from
        salary_to = vacancy.salary_to
        currency = vacancy.salary_currency

        if not currency or currency not in currency_to_rub:
            continue

        if salary_from and salary_to:
            salary = (salary_from + salary_to) / 2
        elif salary_from:
            salary = salary_from
        elif salary_to:
            salary = salary_to
        else:
            continue

        salary_rub = salary * currency_to_rub[currency]
        salaries_by_year[year].append(salary_rub)

    years = sorted(salaries_by_year.keys())
    if not years:
        return

    avg_salaries = [round(statistics.mean(salaries_by_year[year])) for year in years]

    plt.figure(figsize=(10, 6))
    plt.plot(years, avg_salaries, marker='o', color='seagreen')
    plt.title('Динамика уровня зарплат по годам (Аналитик)')
    plt.xlabel('Год')
    plt.ylabel('Средняя зарплата, руб.')
    plt.grid(True)
    plt.tight_layout()

    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    plt.savefig(os.path.join(graph_dir, 'salary_analyst_dynamics.png'))
    plt.close()

def generate_city_salaries_chart():
    city_salaries = defaultdict(list)
    total_vacancies = Vacancy.objects.exclude(salary_from__isnull=True).exclude(salary_from=0).count()

    for vacancy in Vacancy.objects.exclude(salary_from__isnull=True).exclude(salary_from=0):
        city = vacancy.area_name.strip() if vacancy.area_name else 'Не указано'
        city_salaries[city].append(vacancy.salary_from)

    # Порог уменьшен до 0.5%
    min_vacancies = max(1, int(total_vacancies * 0.005))
    filtered_cities = {
        city: salaries
        for city, salaries in city_salaries.items()
        if len(salaries) >= min_vacancies
    }

    if not filtered_cities:
        print("Недостаточно данных для построения графика по городам.")
        return

    city_avg_salaries = {
        city: int(statistics.mean(salaries))
        for city, salaries in filtered_cities.items()
    }

    # Выбираем топ-10 городов по средней зарплате
    top_cities = sorted(city_avg_salaries.items(), key=lambda x: x[1], reverse=True)[:10]
    if not top_cities:
        print("Нет городов с подходящими данными.")
        return

    cities, avg_salaries = zip(*top_cities)

    # Построение графика
    plt.figure(figsize=(10, 6))
    bars = plt.bar(cities, avg_salaries, color='teal')
    plt.title('Топ-10 городов по уровню зарплаты')
    plt.ylabel('Средняя зарплата, руб.')
    plt.xticks(rotation=45, ha='right')

    # Подписи на столбцах
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:,}', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()

    # Сохраняем график
    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    path = os.path.join(graph_dir, 'geo_salary_by_city.png')  # имя файла под шаблон
    plt.savefig(path)
    plt.close()

def generate_city_vacancy_share_chart():
    # Собираем все города
    all_cities = [v.area_name.strip() for v in Vacancy.objects.exclude(area_name__isnull=True).exclude(area_name='')]

    # Подсчёт городов
    top_cities = Counter(all_cities).most_common(10)

    if not top_cities:
        return

    cities, counts = zip(*top_cities)
    total = sum(counts)
    percentages = [count / total * 100 for count in counts]

    # График
    plt.figure(figsize=(8, 8))
    plt.pie(percentages, labels=cities, autopct='%1.1f%%', startangle=140)
    plt.title('Доля вакансий по городам (топ-10)')
    plt.tight_layout()

    # Сохраняем
    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    path = os.path.join(graph_dir, 'city_vacancy_share.png')
    plt.savefig(path)
    plt.close()

#география
def generate_salary_by_city_chart(profession_keywords):
    from main.models import Vacancy  # адаптируй под свою модель

    city_salaries = defaultdict(list)

    for vacancy in Vacancy.objects.all():
        if not any(word.lower() in vacancy.name.lower() for word in profession_keywords):
            continue

        city = vacancy.area_name
        if not city:
            continue

        if vacancy.salary_currency not in currency_to_rub:
            continue

        salary = None
        if vacancy.salary_from and vacancy.salary_to:
            salary = (vacancy.salary_from + vacancy.salary_to) / 2
        elif vacancy.salary_from:
            salary = vacancy.salary_from
        elif vacancy.salary_to:
            salary = vacancy.salary_to

        if salary:
            salary_rub = salary * currency_to_rub[vacancy.salary_currency]
            city_salaries[city].append(salary_rub)

    # Средние зарплаты по городам
    avg_city_salaries = {
        city: round(statistics.mean(salaries))
        for city, salaries in city_salaries.items()
        if len(salaries) >= 5  # фильтр для устойчивости данных
    }

    top_cities = sorted(avg_city_salaries.items(), key=lambda x: x[1], reverse=True)[:10]
    cities, salaries = zip(*top_cities) if top_cities else ([], [])

    if not cities:
        return {}

    # График
    plt.figure(figsize=(12, 6))
    plt.barh(cities[::-1], salaries[::-1], color='teal')
    plt.title('Уровень зарплат по городам (ТОП-10)')
    plt.xlabel('Средняя зарплата (руб)')
    plt.tight_layout()

    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    path = os.path.join(graph_dir, 'salary_by_city_analyst.png')
    plt.savefig(path)
    plt.close()

def generate_vacancy_share_by_city_chart(profession_keywords):
    from main.models import Vacancy

    city_counts = defaultdict(int)
    total = 0

    for vacancy in Vacancy.objects.all():
        if not any(word.lower() in vacancy.name.lower() for word in profession_keywords):
            continue

        city = vacancy.area_name
        if city:
            city_counts[city] += 1
            total += 1

    if total == 0:
        return {}

    # Рассчитываем долю в %
    city_shares = {
        city: round((count / total) * 100, 2)
        for city, count in city_counts.items()
        if count >= total * 0.01  # только города с долей >= 1%
    }

    top_cities = sorted(city_shares.items(), key=lambda x: x[1], reverse=True)[:10]
    cities, shares = zip(*top_cities) if top_cities else ([], [])

    # График
    plt.figure(figsize=(12, 6))
    plt.barh(cities[::-1], shares[::-1], color='darkorange')
    plt.title('Доля вакансий по городам (ТОП-10)')
    plt.xlabel('Доля (%)')
    plt.tight_layout()

    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    path = os.path.join(graph_dir, 'vacancy_share_by_city_analyst.png')
    plt.savefig(path)
    plt.close()

#навыки
def generate_skills_chart():
    # Соберём все навыки, исключив пустые и None
    all_skills = []
    for vacancy in Vacancy.objects.exclude(key_skills__isnull=True).exclude(key_skills=''):
        skills_raw = vacancy.key_skills
        if isinstance(skills_raw, float) and math.isnan(skills_raw):
            continue  # пропускаем NaN

        skills = skills_raw.split('\n')
        for skill in skills:
            skill_clean = skill.strip()
            if skill_clean and skill_clean.lower() != 'nan' and not skill_clean.isspace():
                all_skills.append(skill_clean.title())  # Приводим к нормальному виду

    if not all_skills:
        return

    # Подсчёт
    top_skills = Counter(all_skills).most_common(10)
    skills, counts = zip(*top_skills)

    # График
    plt.figure(figsize=(10, 6))
    bars = plt.bar(skills, counts, color='mediumpurple')
    plt.title('Топ-10 самых востребованных навыков')
    plt.ylabel('Количество упоминаний')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Сохраняем
    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    path = os.path.join(graph_dir, 'skills.png')
    plt.savefig(path)
    plt.close()

def generate_skills_chart_analyst(profession_keywords):
    # Формируем Q-запрос для поиска по всем ключевым словам
    query = Q()
    for kw in profession_keywords:
        query |= Q(name__icontains=kw)

    # Фильтруем вакансии по названию профессии и наличию ключевых навыков
    vacancies = Vacancy.objects.filter(query).exclude(key_skills__isnull=True).exclude(key_skills='')

    all_skills = []
    for vacancy in vacancies:
        skills_raw = vacancy.key_skills
        if isinstance(skills_raw, float) and math.isnan(skills_raw):
            continue

        skills = skills_raw.split('\n')
        for skill in skills:
            skill_clean = skill.strip()
            if skill_clean and skill_clean.lower() != 'nan' and not skill_clean.isspace():
                all_skills.append(skill_clean.title())

    if not all_skills:
        print("Нет подходящих навыков.")
        return

    # Считаем топ-20
    top_skills = Counter(all_skills).most_common(20)
    skills, counts = zip(*top_skills)

    # Строим график
    plt.figure(figsize=(12, 7))
    bars = plt.bar(skills, counts, color='teal')
    plt.title('ТОП-20 навыков по профессии')
    plt.ylabel('Количество упоминаний')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Сохраняем
    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    path = os.path.join(graph_dir, 'skills_analyst.png')
    plt.savefig(path)
    plt.close()


