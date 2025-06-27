
from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('', views.domain_input, name='domain_input'),
    path('results/', views.results_page, name='results_page'),
    path('run/', views.run_automation, name='run_automation'),
]