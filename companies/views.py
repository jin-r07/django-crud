import os
import sqlite3
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .models import Company, Student
from .forms import CompanyForm, StudentForm
from django.conf import settings
from django.http import Http404


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
    # Replace spaces with underscores, leave everything else unchanged
    formatted_company_name = company_name.replace(" ", "_")
    if formatted_company_name:  # Ensure the name is not empty
        db_file_path = os.path.join(settings.MEDIA_ROOT, f'{formatted_company_name}.db')
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()

        # Create the students table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        ''')

        # Commit and close the connection
        conn.commit()
        conn.close()
    else:
        print("Invalid company name provided.")


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
                rename_database(old_name, new_name)

            return redirect('company_list')
        else:
            print("Form errors:", form.errors)
    else:
        form = CompanyForm(instance=company)

    return render(request, 'update_company.html', {'form': form, 'company': company})


def rename_database(old_name, new_name):
    # Replace spaces with underscores, leave everything else unchanged
    formatted_old_name = old_name.replace(" ", "_")
    formatted_new_name = new_name.replace(" ", "_")

    if formatted_old_name and formatted_new_name:
        old_db_file_path = os.path.join(settings.MEDIA_ROOT, f'{formatted_old_name}.db')
        new_db_file_path = os.path.join(settings.MEDIA_ROOT, f'{formatted_new_name}.db')

        if os.path.exists(old_db_file_path):
            os.rename(old_db_file_path, new_db_file_path)
        else:
            print(f"Database file {old_db_file_path} not found. Creating a new one.")
            create_database(new_name)
    else:
        print("Invalid company name. Cannot rename database.")


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


def add_student(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    existing_students = fetch_students_from_company_db(company.name)

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            # Create a student instance without saving to DB
            student = form.save(commit=False)
            student.company = company  # Associate with the company

            # Store student information directly in the company's database
            store_student_in_company_db(company.name, student)

            # Redirect to the same add_student view to show updated student list
            return redirect('add_student', company_id=company.id)
    else:
        form = StudentForm()  # Initialize a blank form for GET request

    # Render the template with the form, company details, and existing students
    return render(request, 'add_student.html', {'form': form, 'company': company, 'students': existing_students })


def fetch_students_from_company_db(company_name):
    sanitized_company_name = company_name.replace(" ", "_").lower()
    db_file_path = os.path.join(settings.MEDIA_ROOT, f'{sanitized_company_name}.db')

    # Connect to the company's database
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Fetch all students from the database, including their IDs
    cursor.execute('SELECT id, name, age FROM students')
    student_records = cursor.fetchall()

    # Close the connection
    conn.close()

    # Convert the records into a list of dictionaries or Student instances
    students = [Student(id=id, name=name, age=age) for id, name, age in student_records]
    
    return students


def store_student_in_company_db(company_name, student):
    # Sanitize the company name for the database file name
    sanitized_company_name = company_name.replace(" ", "_").lower()
    db_file_path = os.path.join(settings.MEDIA_ROOT, f'{sanitized_company_name}.db')

    # Connect to the company's database
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    
    # Insert the student data into the students table
    cursor.execute('''
        INSERT INTO students (name, age)
        VALUES (?, ?)
    ''', (student.name, student.age))

    # Commit and close the connection
    conn.commit()
    conn.close()


def update_student(request, company_id, student_id):
    company = get_object_or_404(Company, id=company_id)
    student = fetch_student_from_company_db(company.name, student_id)  # Fetch student for the specific company

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            update_student_in_company_db(student_id, form.cleaned_data['name'], form.cleaned_data['age'], company.name)
            return redirect('add_student', company_id=company.id)
    else:
        form = StudentForm(initial={'name': student.name, 'age': student.age})

    return render(request, 'update_student.html', {'form': form, 'company': company, 'student': student})


def delete_student(request, company_id, student_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        delete_student_from_company_db(company.name, student_id)
        return redirect('add_student', company_id=company.id)

    return redirect('add_student', company_id=company.id)


def fetch_student_from_company_db(company_name, student_id):
    formatted_company_name = company_name.replace(" ", "_")  # Keep consistent naming
    db_file_path = os.path.join(settings.MEDIA_ROOT, f'{formatted_company_name}.db')

    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Fetch the student by ID
    cursor.execute('SELECT id, name, age FROM students WHERE id = ?', (student_id,))
    student_record = cursor.fetchone()
    conn.close()

    if student_record:
        return Student(id=student_record[0], name=student_record[1], age=student_record[2])
    else:
        raise Http404("Student not found.")


def update_student_in_company_db(student_id, name, age, company_name):
    formatted_company_name = company_name.replace(" ", "_")
    db_file_path = os.path.join(settings.MEDIA_ROOT, f'{formatted_company_name}.db')

    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Update the student in the database
    cursor.execute('UPDATE students SET name = ?, age = ? WHERE id = ?', (name, age, student_id))
    conn.commit()
    conn.close()


def delete_student_from_company_db(company_name, student_id):
    formatted_company_name = company_name.replace(" ", "_")
    db_file_path = os.path.join(settings.MEDIA_ROOT, f'{formatted_company_name}.db')

    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Delete the student from the database
    cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
