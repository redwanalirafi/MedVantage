from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Users(models.Model):

    ROLE_CHOICES = (
        ('patient','patient'),
        ('doctor', 'doctor'),
        ('assistant','assistant'),
        ('admin','admin'),
        ('staff','staff'),
    )
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

    def __str__(self):
        return self.display_name

class Doctor(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    designation = models.CharField(max_length=200)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} : {self.designation}" 


class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE,related_name="appointment_patient")
    doctor = models.ForeignKey(User, on_delete=models.CASCADE,related_name="appointment_doctor")
    date = models.CharField(max_length=50)
    meeting_link=models.CharField(max_length=50,default="no")
    document = models.FileField(upload_to='media/reports',null=True, blank=True)
    prescription = models.TextField(default="", null=True, blank=True)
    fee = models.IntegerField(default=1000)
    review = models.TextField(null=True,blank=True, default="")

    def __str__(self):
        return f"Appointment with {self.doctor} on {self.date}"

class PatientDocs(models.Model):
    appointment_id = models.ForeignKey(Appointment,on_delete=models.CASCADE)
    patient_document = models.FileField(upload_to='media/reports')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
    












