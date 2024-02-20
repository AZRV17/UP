from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=50)
    login = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.login


class ElectronicCard(models.Model):

    medical_card = models.CharField(max_length=50)
    result = models.CharField(max_length=50)
    diagnosis = models.CharField(max_length=50)
    treatment = models.CharField(max_length=50)


class Patient(models.Model):
    surname = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    electronic_card = models.ForeignKey(ElectronicCard, on_delete=models.CASCADE, null=True)
    role = models.OneToOneField(Role, on_delete=models.CASCADE)

    def __str__(self):
        return self.surname


class Doctor(models.Model):
    surname = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    direction = models.CharField(max_length=50)
    role = models.OneToOneField(Role, on_delete=models.CASCADE)

    def __str__(self):
        return self.surname


class Calendar(models.Model):
    schedule = models.CharField(max_length=50)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

    def __str__(self):
        return self.schedule


class Recipe(models.Model):
    treatment = models.CharField(max_length=50)
    denomination = models.CharField(max_length=50)
    deadline = models.DateField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.denomination


class Record(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def __str__(self):
        return self.patient.name
