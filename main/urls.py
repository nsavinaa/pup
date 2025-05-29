from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # главная страница
    path('statistics/', views.statistics, name='statistics'),  # статистика
    path('demand/', views.demand, name='demand'),
    path('geography/', views.geography, name='geography'),
    path('skills/', views.skills, name='skills'),
    path('vacancies/', views.vacancies, name='vacancies'),
]
