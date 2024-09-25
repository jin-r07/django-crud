from django import forms
from .models import Company, Student

# Form for creating and updating Company instances.
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company  # Specify the model this form is associated with.
        fields = ['name']  # Only the 'name' field will be included in the form.


# Form for creating and updating Student instances.
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student  # Specify the model this form is associated with.
        fields = ['name', 'age']  # Include 'name' and 'age' fields in the form.
