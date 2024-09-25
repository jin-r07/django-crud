from django.urls import path
from .views import login_view, company_list

urlpatterns = [
    path('', login_view, name='login'),
    path('companies/', company_list, name='company_list'),
]