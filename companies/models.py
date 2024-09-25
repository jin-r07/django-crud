from django.db import models

# Model representing a company. Each company has a unique name.
class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Company name must be unique across all companies.

    def __str__(self):
        # Return the name of the company when referenced as a string, for easy identification in admin or queries.
        return self.name


# Model representing a student. Each student is associated with a specific company.
class Student(models.Model):
    name = models.CharField(max_length=100)  # Student's name (max 100 characters).
    age = models.IntegerField()  # Age of the student as an integer field.
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,  # If the company is deleted, all its associated students are also deleted.
        related_name='students'  # Allows accessing all students of a company using `company.students` in queries.
    )

    def __str__(self):
        # Return the student's name and age in a formatted string, useful for display in admin or templates.
        return f"{self.name} ({self.age})"
