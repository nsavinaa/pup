from django.shortcuts import render
from main.models import Vacancy
from collections import defaultdict
import json
from collections import Counter
import pandas as pd
from django.shortcuts import render
from main.models import Vacancy
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def index(request):
    return render(request, 'index.html')

def statistics(request):
    '''salary_sum = defaultdict(float)
    salary_count = defaultdict(int)
    vacancy_count = defaultdict(int)

    vacancies = Vacancy.objects.all()

    for v in vacancies:
        if v.published_at:
            year = v.published_at.year
            vacancy_count[year] += 1
            if v.salary_from and v.salary_to:
                avg_salary = (v.salary_from + v.salary_to) / 2
                salary_sum[year] += avg_salary
                salary_count[year] += 1

    salary_data = {}
    for year in salary_sum:
        salary_data[year] = round(salary_sum[year] / salary_count[year], 2) if salary_count[year] > 0 else 0

    context = {
        'salary_data': salary_data,
        'vacancy_data': dict(vacancy_count),
        'salary_data_json': json.dumps(salary_data),
        'vacancy_data_json': json.dumps(dict(vacancy_count)),
    }
    return render(request, 'statistics.html', context)'''
    return render(request, 'statistics.html')

def demand(request):
    '''salary_sum = defaultdict(float)
    salary_count = defaultdict(int)
    vacancy_count = defaultdict(int)

    for v in Vacancy.objects.all():
        if v.published_at:
            year = v.published_at.year
            vacancy_count[year] += 1
            if v.salary_from and v.salary_to:
                avg_salary = (v.salary_from + v.salary_to) / 2
                salary_sum[year] += avg_salary
                salary_count[year] += 1

    salary_data = {year: round(salary_sum[year] / salary_count[year], 2) for year in salary_sum}

    context = {
        'salary_data_json': json.dumps(salary_data),
        'vacancy_data_json': json.dumps(dict(vacancy_count)),
    }
    return render(request, 'demand.html', context)'''
    return render(request, 'demand.html')

def geography(request):
    '''city_salary = defaultdict(list)
    city_count = defaultdict(int)
    total_vacancies = Vacancy.objects.count()

    for v in Vacancy.objects.all():
        if v.area_name:
            city_count[v.area_name] += 1
            if v.salary_from and v.salary_to:
                avg = (v.salary_from + v.salary_to) / 2
                city_salary[v.area_name].append(avg)

    # Средняя зарплата по городам (только города с 50+ вакансий)
    avg_salaries = {
        city: round(sum(salaries) / len(salaries), 2)
        for city, salaries in city_salary.items() if city_count[city] >= 50
    }

    # Топ-10 городов по средней зарплате
    top_salary_cities = dict(sorted(avg_salaries.items(), key=lambda x: x[1], reverse=True)[:10])

    # Доля вакансий по городам (топ-10)
    city_shares = {
        city: round(count / total_vacancies, 4)
        for city, count in city_count.items()
    }
    top_share_cities = dict(sorted(city_shares.items(), key=lambda x: x[1], reverse=True)[:10])

    context = {
        'top_salary_cities': json.dumps(top_salary_cities),
        'top_share_cities': json.dumps(top_share_cities),
    }
    return render(request, 'geography.html', context)'''
    return render(request, 'geography.html')


def skills(request):
    '''skills_counter = Counter()

    for vacancy in Vacancy.objects.all():
        if vacancy.key_skills:
            skills = [s.strip() for s in vacancy.key_skills.split('\n') if s.strip()]
            skills_counter.update(skills)

    top_skills = dict(skills_counter.most_common(10))

    context = {
        'top_skills': json.dumps(top_skills),
    }
    return render(request, 'skills.html', context)'''
    return render(request, 'skills.html')

def vacancies(request):
    # Получаем последние 20 вакансий, отсортированных по дате публикации (по убыванию)
    vacancies = Vacancy.objects.filter(is_relevant=True).order_by('-published_at')[:20]

    context = {
        'vacancies': vacancies,
    }
    return render(request, 'vacancies.html', context)
