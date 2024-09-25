from django.urls import path
from .views import login_view, company_list, update_company, delete_company, add_student

urlpatterns = [
    path('', login_view, name='login'),
    path('companies/', company_list, name='company_list'),
    path('update/<int:company_id>/', update_company, name='update_company'),
    path('delete/<int:company_id>/', delete_company, name='delete_company'),

    path('add_student/<int:company_id>/', add_student, name='add_student'),
]