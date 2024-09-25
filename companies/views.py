import os
import sqlite3
from django.shortcuts import render, redirect
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

            company_name = company.name
            sanitized_company_name = company_name.replace(" ", "_").lower()
            db_file_path = os.path.join(settings.MEDIA_ROOT, f'{sanitized_company_name}.db')

            conn = sqlite3.connect(db_file_path)
            conn.close()

            return redirect('company_list')
    else:
        form = CompanyForm()

    companies = Company.objects.all()

    return render(request, 'company_list.html', {'companies': companies, 'form': form})