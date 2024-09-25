import os
import sqlite3
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .models import Company
from .forms import CompanyForm
from django.conf import settings


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('company_list')
            else:
                return render(request, 'login.html', {'error': 'You are not authorized to access this page.'})
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')


def company_list(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            create_database(company.name)
            return redirect('company_list')
    else:
        form = CompanyForm()

    companies = Company.objects.all()
    return render(request, 'company_list.html', {'companies': companies, 'form': form})


def create_database(company_name):
    sanitized_company_name = company_name.replace(" ", "_").lower()
    db_file_path = os.path.join(settings.MEDIA_ROOT, f'{sanitized_company_name}.db')
    conn = sqlite3.connect(db_file_path)
    conn.close()


def update_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    old_name = company.name
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        print("Form data:", request.POST)
        if form.is_valid():
            company = form.save()
            new_name = company.name

            if old_name != new_name:
                delete_database(old_name)
                create_database(new_name)

            return redirect('company_list')
        else:
            print("Form errors:", form.errors)
    else:
        form = CompanyForm(instance=company)

    return render(request, 'update_company.html', {'form': form, 'company': company})


def delete_database(company_name):
    sanitized_company_name = company_name.replace(" ", "_").lower()
    db_file_path = os.path.join(settings.MEDIA_ROOT, f'{sanitized_company_name}.db')
    if os.path.exists(db_file_path):
        os.remove(db_file_path)
        

def delete_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    delete_database(company.name)
    company.delete()
    return redirect('company_list')