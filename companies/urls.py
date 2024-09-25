from django.urls import path
from .views import login_view, company_list, update_company, delete_company, add_student, update_student, delete_student

urlpatterns = [
    path('', login_view, name='login'),
    path('companies/', company_list, name='company_list'),
    path('update/<int:company_id>/', update_company, name='update_company'),
    path('delete/<int:company_id>/', delete_company, name='delete_company'),

    path('add_student/<int:company_id>/', add_student, name='add_student'),
    path('company/<int:company_id>/student/<int:student_id>/edit/', update_student, name='edit_student'),
    path('company/<int:company_id>/student/<int:student_id>/delete/', delete_student, name='delete_student'),
]