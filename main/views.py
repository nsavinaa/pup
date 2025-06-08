import json
from django.shortcuts import render
from django.db.models import F, FloatField, Value, Avg, Count
from django.db.models.functions import Coalesce, ExtractYear
from main.models import Vacancy, MainPage
from django.db.models import ExpressionWrapper

# Курсы валют — актуализируй при необходимости
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
            avg_salary=Coalesce(
                Avg(
                    (F('salary_from') + F('salary_to')) / 2,
                    output_field=FloatField()
                ),
                Value(0),
                output_field=FloatField()
            ),
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

    qs = Vacancy.objects.exclude(area_name__isnull=True).exclude(salary_currency__isnull=True).exclude(salary_currency='') \
        .values('area_name', 'salary_currency') \
        .annotate(
            avg_salary_raw=ExpressionWrapper(
                (F('salary_from') + F('salary_to')) / 2,
                output_field=FloatField()
            ),
            vacancy_count=Count('id')
        )

    city_salary = {}

    for vac in qs:
        if vac['avg_salary_raw'] is None:
            continue  # пропускаем вакансии без зарплаты

        currency = vac['salary_currency']
        if currency not in currency_to_rub:
            raise ValueError(f"Неизвестная валюта: {currency}")

        salary_in_rub = vac['avg_salary_raw'] * currency_to_rub[currency]
        city = vac['area_name']

        if city not in city_salary:
            city_salary[city] = {'salary_sum': 0, 'count': 0, 'vacancy_count': 0}
        city_salary[city]['salary_sum'] += salary_in_rub * vac['vacancy_count']
        city_salary[city]['count'] += vac['vacancy_count']
        city_salary[city]['vacancy_count'] += vac['vacancy_count']

    filtered_cities = {city: data for city, data in city_salary.items() if data['vacancy_count'] >= 50}

    avg_salary_cities = {city: round(data['salary_sum'] / data['count'], 2) for city, data in filtered_cities.items()}

    share_cities = {city: round(data['vacancy_count'] / total_vacancies, 4) for city, data in filtered_cities.items()}

    top_salary_cities = dict(sorted(avg_salary_cities.items(), key=lambda x: x[1], reverse=True)[:10])
    top_share_cities = dict(sorted(share_cities.items(), key=lambda x: x[1], reverse=True)[:10])

    context = {
        'top_salary_cities': json.dumps(top_salary_cities),
        'top_share_cities': json.dumps(top_share_cities),
    }
    return render(request, 'geography.html', context)


def skills(request):
    from collections import Counter

    vacancies = Vacancy.objects.exclude(key_skills__isnull=True).order_by('-published_at')[:10000]

    skills_counter = Counter()
    for vac in vacancies:
        skills = [s.strip() for s in vac.key_skills.split('\n') if s.strip() and s.strip().lower() != 'nan']
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
