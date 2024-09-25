import os
import sqlite3
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .models import Company, Student
from .forms import CompanyForm, StudentForm
from django.conf import settings
from django.http import Http404

# View for handling login requests and user authentication.
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser: # Super user only
                login(request, user)
                return redirect('company_list')  # Redirect to company list after successful login
            else:
                return render(request, 'login.html', {'error': 'You are not authorized to access this page.'})
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')


# View for listing all companies and adding new ones. Also handles form submission.
def company_list(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            create_database(company.name)  # Create a unique database for each company
            return redirect('company_list')
    else:
        form = CompanyForm()

    companies = Company.objects.all()  # Fetch all existing companies
    return render(request, 'company_list.html', {'companies': companies, 'form': form})


# Function to create a new SQLite database for a company, replacing spaces in the name with underscores.
def create_database(company_name):
    formatted_company_name = company_name.replace(" ", "_")
    if formatted_company_name:  # Ensure the name is not empty
        db_file_path = os.path.join(settings.MEDIA_ROOT, f'{formatted_company_name}.db')
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()

        # Create a table for students specific to this company if it doesn't already exist.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        ''')

        conn.commit()  # Commit changes to the database
        conn.close()   # Close the database connection
    else:
        print("Invalid company name provided.")


# View for updating an existing company and renaming its associated database if needed.
def update_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    old_name = company.name  # Save the old name to compare later
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            company = form.save()
            new_name = company.name

            # If the company name changes, rename the associated database file.
            if old_name != new_name:
                rename_database(old_name, new_name)

            return redirect('company_list')
    else:
        form = CompanyForm(instance=company)

    return render(request, 'update_company.html', {'form': form, 'company': company})


# Function to rename the database when a company's name is changed.
def rename_database(old_name, new_name):
    formatted_old_name = old_name.replace(" ", "_")
    formatted_new_name = new_name.replace(" ", "_")

    if formatted_old_name and formatted_new_name:
        old_db_file_path = os.path.join(settings.MEDIA_ROOT, f'{formatted_old_name}.db')
        new_db_file_path = os.path.join(settings.MEDIA_ROOT, f'{formatted_new_name}.db')

        # Rename the database file if it exists.
        if os.path.exists(old_db_file_path):
            os.rename(old_db_file_path, new_db_file_path)
        else:
            print(f"Database file {old_db_file_path} not found. Creating a new one.")
            create_database(new_name)
    else:
        print("Invalid company name. Cannot rename database.")


# Function to delete a company's associated database.
def delete_database(company_name):
    sanitized_company_name = company_name.replace(" ", "_").lower()
    db_file_path = os.path.join(settings.MEDIA_ROOT, f'{sanitized_company_name}.db')
    if os.path.exists(db_file_path):
        os.remove(db_file_path)


# View for deleting a company and its associated database.
def delete_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    delete_database(company.name)  # Remove associated database
    company.delete()  # Delete the company from the main database
    return redirect('company_list')


# View for adding a student to a specific company, displaying existing students, and saving new ones.
def add_student(request, company_id):
    company = get_object_or_404(Company, id=company_id)  # Fetch the company by ID
    existing_students = fetch_students_from_company_db(company.name)  # Fetch students specific to this company

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.company = company  # Associate the student with the company

            # Save the student to the company's specific SQLite database
            store_student_in_company_db(company.name, student)
            return redirect('add_student', company_id=company.id)
    else:
        form = StudentForm()

    return render(request, 'add_student.html', {'form': form, 'company': company, 'students': existing_students})


# Helper function to fetch all students from a company's specific SQLite database.
def fetch_students_from_company_db(company_name):
    sanitized_company_name = company_name.replace(" ", "_").lower()
    db_file_path = os.path.join(settings.MEDIA_ROOT, f'{sanitized_company_name}.db')

    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Fetch all students from the 'students' table in the company's database.
    cursor.execute('SELECT id, name, age FROM students')
    student_records = cursor.fetchall()

    conn.close()

    # Convert the records into a list of student objects.
    students = [Student(id=id, name=name, age=age) for id, name, age in student_records]
    return students


# Helper function to store a new student in a company's specific SQLite database.
def store_student_in_company_db(company_name, student):
    sanitized_company_name = company_name.replace(" ", "_").lower()
    db_file_path = os.path.join(settings.MEDIA_ROOT, f'{sanitized_company_name}.db')

    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Insert the new student's data into the 'students' table.
    cursor.execute('''
        INSERT INTO students (name, age)
        VALUES (?, ?)
    ''', (student.name, student.age))

    conn.commit()
    conn.close()


# View for updating a student's details within a specific company's database.
def update_student(request, company_id, student_id):
    company = get_object_or_404(Company, id=company_id)
    student = fetch_student_from_company_db(company.name, student_id)  # Fetch student from company-specific DB

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            # Update student information in the company's database
            update_student_in_company_db(student_id, form.cleaned_data['name'], form.cleaned_data['age'], company.name)
            return redirect('add_student', company_id=company.id)
    else:
        form = StudentForm(initial={'name': student.name, 'age': student.age})

    return render(request, 'update_student.html', {'form': form, 'company': company, 'student': student})


# View for deleting a student from a company's database.
def delete_student(request, company_id, student_id):
    company = get_object_or_404(Company, id=company_id)
    if request.method == 'POST':
        delete_student_from_company_db(company.name, student_id)  # Remove student from the company's database
        return redirect('add_student', company_id=company.id)

    return redirect('add_student', company_id=company.id)


# Helper function to fetch a specific student by ID from a company's SQLite database.
def fetch_student_from_company_db(company_name, student_id):
    formatted_company_name = company_name.replace(" ", "_")
    db_file_path = os.path.join(settings.MEDIA_ROOT, f'{formatted_company_name}.db')

    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Fetch the student from the database using their ID.
    cursor.execute('SELECT id, name, age FROM students WHERE id = ?', (student_id,))
    student_record = cursor.fetchone()
    conn.close()

    if student_record:
        return Student(id=student_record[0], name=student_record[1], age=student_record[2])
    else:
        raise Http404("Student not found.")


# Helper function to update a student's details in a company's SQLite database.
def update_student_in_company_db(student_id, name, age, company_name):
    formatted_company_name = company_name.replace(" ", "_")
    db_file_path = os.path.join(settings.MEDIA_ROOT, f'{formatted_company_name}.db')

    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Update the student's details in the 'students' table.
    cursor.execute('UPDATE students SET name = ?, age = ? WHERE id = ?', (name, age, student_id))
    conn.commit()
    conn.close()


# Helper function to delete a student from a company's SQLite database.
def delete_student_from_company_db(company_name, student_id):
    formatted_company_name = company_name.replace(" ", "_")
    db_file_path = os.path.join(settings.MEDIA_ROOT, f'{formatted_company_name}.db')

    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Delete the student record from the database.
    cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
