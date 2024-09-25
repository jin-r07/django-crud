from django.urls import path
from .views import login_view, company_list, update_company, delete_company, add_student, update_student, delete_student

# Define URL patterns for the application
urlpatterns = [
    # Login view for the application
    path('', login_view, name='login'),

    # URL for viewing the list of companies
    path('companies/', company_list, name='company_list'),

    # URL for updating a specific company by its ID
    path('update/<int:company_id>/', update_company, name='update_company'),

    # URL for deleting a specific company by its ID
    path('delete/<int:company_id>/', delete_company, name='delete_company'),

    # URL for adding a new student to a specific company by the company's ID
    path('add_student/<int:company_id>/', add_student, name='add_student'),

    # URL for editing a specific student of a specific company
    path('company/<int:company_id>/student/<int:student_id>/edit/', update_student, name='edit_student'),

    # URL for deleting a specific student of a specific company
    path('company/<int:company_id>/student/<int:student_id>/delete/', delete_student, name='delete_student'),
]
