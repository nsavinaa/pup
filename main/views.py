import requests
from datetime import datetime, timedelta
from django.shortcuts import render
from main.models import Vacancy, MainPage
from django.conf import settings
import os

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
}

def index(request):
    main_page = MainPage.objects.first()  # если несколько записей — меняй по ID или фильтру
    return render(request, 'index.html', {'main_page': main_page})

def statistics(request):
    return render(request, 'statistics.html')

def demand(request):
    return render(request, 'demand.html')


def geography(request):
    return render(request, 'geography.html')


def skills(request):
    return render(request, 'skills.html')

def vacancies(request):
    profession_keywords = ['аналитик', 'data analyst', 'бизнес-аналитик', 'bi-аналитик']
    search_text = ' OR '.join(profession_keywords)
    url = 'https://api.hh.ru/vacancies'
    date_from = (datetime.now() - timedelta(days=1)).isoformat()

    params = {
        'text': search_text,
        'area': 113,  # Россия
        'specialization': 1,  # IT
        'date_from': date_from,
        'per_page': 10,
        'order_by': 'publication_time'
    }

    response = requests.get(url, params=params)
    vacancies = []

    if response.status_code == 200:
        for item in response.json().get('items', []):
            vacancy_id = item['id']
            detail_url = f'https://api.hh.ru/vacancies/{vacancy_id}'
            detail_resp = requests.get(detail_url)

            if detail_resp.status_code == 200:
                detail = detail_resp.json()
                salary = detail.get('salary') or {}
                employer = detail.get('employer') or {}
                area = detail.get('area') or {}

                vacancy = {
                    'name': detail.get('name'),
                    'description': detail.get('description', '').strip()[:500],
                    'skills': ', '.join([s['name'] for s in detail.get('key_skills', [])]),
                    'company': employer.get('name', 'Не указана'),
                    'salary_from': salary.get('from'),
                    'salary_to': salary.get('to'),
                    'salary_currency': salary.get('currency'),
                    'area_name': area.get('name', 'Не указано'),
                    'published_at': detail.get('published_at', '')[:10],
                }
                vacancies.append(vacancy)

    return render(request, 'vacancies.html', {'vacancies': vacancies})
    # Последние 20 вакансий по дате публикации

