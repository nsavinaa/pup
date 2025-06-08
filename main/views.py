from django.db.models import Avg, Count, F, FloatField, Value
import json
from django.shortcuts import render
from main.models import Vacancy, MainPage, StatSection
from django.db.models import Count, Avg, F, FloatField
from django.db.models.functions import ExtractYear, Coalesce
# Курсы валют — актуализируй при необходимости
currency_to_rub = {
    'RUR': 1,
    'USD': 75,
    'EUR': 90,
    'KZT': 0.18,
    # Добавляй другие валюты, если нужно
}

def index(request):
    main_page = MainPage.objects.first()  # если несколько записей — меняй по ID или фильтру
    return render(request, 'index.html', {'main_page': main_page})

def statistics(request):
    # Сначала аннотируем среднюю зарплату для каждой вакансии
    qs = Vacancy.objects.annotate(
        year=ExtractYear('published_at'),
        avg_salary_per_vacancy=Coalesce(
            (F('salary_from') + F('salary_to')) / 2,
            Value(0),
            output_field=FloatField()
        )
    ).values('year').annotate(
        avg_salary=Coalesce(Avg('avg_salary_per_vacancy'), Value(0), output_field=FloatField()),
        vacancy_count=Count('id')
    ).order_by('year')

    salary_data = {entry['year']: round(entry['avg_salary'], 2) for entry in qs if entry['year'] is not None}
    vacancy_data = {entry['year']: entry['vacancy_count'] for entry in qs if entry['year'] is not None}

    context = {
        'salary_data_json': json.dumps(salary_data),
        'vacancy_data_json': json.dumps(vacancy_data),
    }
    return render(request, 'statistics.html', context)

def demand(request):
    qs = Vacancy.objects.annotate(year=ExtractYear('published_at')) \
        .values('year') \
        .annotate(
            avg_salary=Coalesce(Avg((F('salary_from') + F('salary_to')) / 2, output_field=FloatField()), 0),
            vacancy_count=Count('id')
        ).order_by('year')

    salary_data = {entry['year']: round(entry['avg_salary'], 2) for entry in qs if entry['year'] is not None}
    vacancy_data = {entry['year']: entry['vacancy_count'] for entry in qs if entry['year'] is not None}

    context = {
        'salary_data_json': json.dumps(salary_data),
        'vacancy_data_json': json.dumps(vacancy_data),
    }
    return render(request, 'demand.html', context)

def geography(request):
    total_vacancies = Vacancy.objects.count()
    # Средняя зарплата и количество вакансий по городам
    qs = Vacancy.objects.values('area_name') \
        .annotate(
            avg_salary=Coalesce(Avg((F('salary_from') + F('salary_to')) / 2, output_field=FloatField()), 0),
            vacancy_count=Count('id')
        ).filter(area_name__isnull=False).order_by('-vacancy_count')

    # Фильтрация по минимуму вакансий (например, 50)
    filtered = [c for c in qs if c['vacancy_count'] >= 50]

    top_salary_cities = dict(sorted(
        [(c['area_name'], round(c['avg_salary'], 2)) for c in filtered],
        key=lambda x: x[1], reverse=True
    )[:10])

    top_share_cities = dict(sorted(
        [(c['area_name'], round(c['vacancy_count'] / total_vacancies, 4)) for c in filtered],
        key=lambda x: x[1], reverse=True
    )[:10])

    context = {
        'top_salary_cities': json.dumps(top_salary_cities),
        'top_share_cities': json.dumps(top_share_cities),
    }
    return render(request, 'geography.html', context)

def skills(request):
    from collections import Counter

    # Возьмём только последние 10000 вакансий, чтобы не грузить всё
    vacancies = Vacancy.objects.exclude(key_skills__isnull=True).order_by('-published_at')[:10000]

    skills_counter = Counter()
    for vac in vacancies:
        skills = [s.strip() for s in vac.key_skills.split('\n') if s.strip()]
        skills_counter.update(skills)

    top_skills = dict(skills_counter.most_common(10))

    context = {
        'top_skills': json.dumps(top_skills),
    }
    return render(request, 'skills.html', context)

def vacancies(request):
    # Последние 20 вакансий по дате публикации
    vacancies = Vacancy.objects.filter(is_relevant=True).order_by('-published_at')[:20]

    context = {
        'vacancies': vacancies,
    }

    return render(request, 'vacancies.html', context)
