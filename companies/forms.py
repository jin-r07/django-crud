from django import forms
from .models import Company, Student


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name']


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'age']