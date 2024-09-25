from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    

class Student(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    age = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.age})"