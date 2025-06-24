import os
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
from django.conf import settings
from main.models import Vacancy

def generate_vacancy_dynamics_table(profession_keywords=None):
    years = []

    for vacancy in Vacancy.objects.all():
        published_at = vacancy.published_at
        name = vacancy.name

        if not published_at:
            continue

        if profession_keywords:
            if not any(keyword.lower() in (name or '').lower() for keyword in profession_keywords):
                continue

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

    table_data = [['Год', 'Количество вакансий']]
    for year, count in zip(sorted_years, counts):
        table_data.append([str(year), str(count)])

    fig, ax = plt.subplots(figsize=(8, len(table_data)*0.5))
    ax.axis('off')
    table = ax.table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)

    title = 'Таблица: Динамика количества вакансий по годам'
    if profession_keywords:
        title += f' — профессия: {profession_keywords[0].capitalize()}'

    plt.title(title, fontsize=14, pad=20)

    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    filename = 'table_vacancy_dynamics_analyst.png'
    path = os.path.join(graph_dir, filename)

    plt.savefig(path, bbox_inches='tight')
    plt.close()

def generate_salary_dynamics_table(profession_keywords=None):
    salary_sums = {}
    counts = {}

    for vacancy in Vacancy.objects.all():
        published_at = vacancy.published_at
        name = vacancy.name

        if not published_at or (vacancy.salary_from is None and vacancy.salary_to is None):
            continue

        if profession_keywords:
            if not any(keyword.lower() in (name or '').lower() for keyword in profession_keywords):
                continue

        # Берём среднюю зарплату вакансии
        salary_from = vacancy.salary_from or 0
        salary_to = vacancy.salary_to or 0
        salary_avg = (salary_from + salary_to) / 2 if (salary_from and salary_to) else max(salary_from, salary_to)

        if salary_avg == 0:
            continue

        if isinstance(published_at, str):
            try:
                year = datetime.strptime(published_at[:10], '%Y-%m-%d').year
            except Exception:
                continue
        else:
            try:
                year = published_at.year
            except Exception:
                continue

        salary_sums[year] = salary_sums.get(year, 0) + salary_avg
        counts[year] = counts.get(year, 0) + 1

    if not counts:
        return

    sorted_years = sorted(counts.keys())
    avg_salaries = [round(salary_sums[year] / counts[year], 2) for year in sorted_years]

    table_data = [['Год', 'Средняя зарплата']]
    for year, avg_salary in zip(sorted_years, avg_salaries):
        table_data.append([str(year), str(avg_salary)])

    fig, ax = plt.subplots(figsize=(8, len(table_data)*0.5))
    ax.axis('off')
    table = ax.table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)

    title = 'Таблица: Динамика средней зарплаты по годам'
    if profession_keywords:
        title += f' — профессия: {profession_keywords[0].capitalize()}'

    plt.title(title, fontsize=14, pad=20)

    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    filename = 'table_salary_dynamics_analyst.png'
    path = os.path.join(graph_dir, filename)

    plt.savefig(path, bbox_inches='tight')
    plt.close()

def generate_salary_by_city_table(profession_keywords=None):
    salary_sums = {}
    counts = {}

    for vacancy in Vacancy.objects.all():
        area_name = vacancy.area_name
        name = vacancy.name
        if not area_name or (vacancy.salary_from is None and vacancy.salary_to is None):
            continue

        if profession_keywords:
            if not any(keyword.lower() in (name or '').lower() for keyword in profession_keywords):
                continue

        salary_from = vacancy.salary_from or 0
        salary_to = vacancy.salary_to or 0
        salary_avg = (salary_from + salary_to) / 2 if (salary_from and salary_to) else max(salary_from, salary_to)

        if salary_avg == 0:
            continue

        salary_sums[area_name] = salary_sums.get(area_name, 0) + salary_avg
        counts[area_name] = counts.get(area_name, 0) + 1

    if not counts:
        return

    avg_salaries = {city: salary_sums[city] / counts[city] for city in counts}
    sorted_cities = sorted(avg_salaries.items(), key=lambda x: x[1], reverse=True)[:20]

    table_data = [['Город', 'Средняя зарплата']]
    for city, avg_salary in sorted_cities:
        table_data.append([city, str(round(avg_salary, 2))])

    fig, ax = plt.subplots(figsize=(10, len(table_data)*0.5))
    ax.axis('off')
    table = ax.table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)

    title = 'Таблица: Уровень зарплат по городам (топ 20)'
    if profession_keywords:
        title += f' — профессия: {profession_keywords[0].capitalize()}'

    plt.title(title, fontsize=14, pad=20)

    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    filename = 'table_salary_by_city.png'
    path = os.path.join(graph_dir, filename)

    plt.savefig(path, bbox_inches='tight')
    plt.close()

def generate_vacancy_share_by_city_table(profession_keywords=None):
    city_counts = {}
    total = 0

    for vacancy in Vacancy.objects.all():
        area_name = vacancy.area_name
        name = vacancy.name
        if not area_name:
            continue

        if profession_keywords:
            if not any(keyword.lower() in (name or '').lower() for keyword in profession_keywords):
                continue

        city_counts[area_name] = city_counts.get(area_name, 0) + 1
        total += 1

    if total == 0:
        return

    sorted_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    table_data = [['Город', 'Доля вакансий (%)']]
    for city, count in sorted_cities:
        share = round(count / total * 100, 2)
        table_data.append([city, str(share)])

    fig, ax = plt.subplots(figsize=(10, len(table_data)*0.5))
    ax.axis('off')
    table = ax.table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)

    title = 'Таблица: Доля вакансий по городам (топ 20)'
    if profession_keywords:
        title += f' — профессия: {profession_keywords[0].capitalize()}'

    plt.title(title, fontsize=14, pad=20)

    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    filename = 'table_vacancy_share_by_city_analyst.png'
    path = os.path.join(graph_dir, filename)

    plt.savefig(path, bbox_inches='tight')
    plt.close()

def generate_top_skills_table(profession_keywords=None):
    # Навыки хранятся в key_skills — список через запятую
    from collections import defaultdict

    skill_counts_by_year = defaultdict(lambda: defaultdict(int))

    for vacancy in Vacancy.objects.all():
        published_at = vacancy.published_at
        name = vacancy.name
        skills = vacancy.key_skills

        if not published_at or not skills:
            continue

        if profession_keywords:
            if not any(keyword.lower() in (name or '').lower() for keyword in profession_keywords):
                continue

        if isinstance(published_at, str):
            try:
                year = datetime.strptime(published_at[:10], '%Y-%m-%d').year
            except Exception:
                continue
        else:
            try:
                year = published_at.year
            except Exception:
                continue

        skill_list = [s.strip().lower() for s in skills.split(',') if s.strip()]
        for skill in skill_list:
            skill_counts_by_year[year][skill] += 1

    if not skill_counts_by_year:
        return

    # Возьмем последние несколько лет (например, 3) или все
    years = sorted(skill_counts_by_year.keys())
    if len(years) > 3:
        years = years[-3:]

    # Для каждого года берём топ 20 навыков
    table_data = [['Навык'] + [str(y) for y in years]]

    # Соберем общий список навыков за эти года (топ 20 по сумме)
    total_skill_counts = defaultdict(int)
    for y in years:
        for skill, count in skill_counts_by_year[y].items():
            total_skill_counts[skill] += count

    top_skills = sorted(total_skill_counts.items(), key=lambda x: x[1], reverse=True)[:20]

    for skill, _ in top_skills:
        row = [skill]
        for y in years:
            count = skill_counts_by_year[y].get(skill, 0)
            row.append(str(count))
        table_data.append(row)

    fig, ax = plt.subplots(figsize=(12, len(table_data)*0.4))
    ax.axis('off')
    table = ax.table(cellText=table_data, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    title = 'Таблица: Топ-20 навыков по годам'
    if profession_keywords:
        title += f' — профессия: {profession_keywords[0].capitalize()}'

    plt.title(title, fontsize=14, pad=20)

    graph_dir = os.path.join(settings.MEDIA_ROOT, 'graphs')
    os.makedirs(graph_dir, exist_ok=True)
    filename = 'table_top_skills_analyst.png'
    path = os.path.join(graph_dir, filename)

    plt.savefig(path, bbox_inches='tight')
    plt.close()