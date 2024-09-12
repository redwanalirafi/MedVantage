import os
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
from .models import *
from .decorators import *
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from  .email_template import *
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


from io import BytesIO
# from django.template.loader import get_template
# from xhtml2pdf import pisa
# Create your views here.

def index(request):
    return render(request,"index2.html")

def user_register(request):
    if request.method == 'POST':
        print("POST")
        form = SignupForm(request.POST)
        if form.is_valid():
            print("VALID")
            form.save()
            messages.success(request, '<p style="color:green">Registration Successfull<p>')
            #return redirect('login/')
        else:
            print(form.errors)  # Prints the form errors to the console
            messages.error(request, f'Please correct the errors below.{form.errors}')
    else:
        form = SignupForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if Doctor.objects.filter(user=user).exists():
                    return redirect('doctor_home')
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def user_dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def see_doctors(request):
    doctors_query = Doctor.objects.filter(status=True)

    context = {
        "doctors" : doctors_query
    }
    for i in doctors_query:
        print(i.user.first_name)
    return render(request, 'doctors.html',context)

@login_required
def create_appointment(request, pk):
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, request.FILES)
        if form.is_valid():
            Appointment = form.save(commit=False)
            Appointment.patient = User.objects.get(username=request.user.username)  # Automatically assign the logged-in user as the patient
            Appointment.doctor = User.objects.get(username=pk)  # Set the doctor from the URL parameter (e.g., Dr. ABC)
            Appointment.meeting_link = "no"
            Appointment.save()
            return redirect('success_appointment')  # Redirect to success page after booking
    else:

        form = AppointmentForm()

    return render(request, 'appointment.html', {'form': form, 'user': request.user})

def admin_panel(request):
    return render(request, 'base_admin.html')

@login_required
def success_appointment(request):
    return render(request,"success_appointment.html")

@login_required
def success_appointment_doc(request):
    return render(request,"success_appointment_doc.html")

def admin_manage_users(request):
    obj= User.objects.all()

    context={
        "tatal_users" : obj.count(),
        "data" : obj
    }
    return render(request, 'admin_manage_users.html' ,context=context)

def add_doctor(request):
    form = AddDoctorForm()
    return render(request, 'add_doctor.html' ,context={'form' : form})


@login_required
@doctor_required
def doctor_home(request):
    my_appointments=Appointment.objects.filter(doctor=request.user,meeting_link="no")
    # print(f"username: {request.user.username}" )
    
    context={
        "appointments" : my_appointments
    }
    return render(request, 'doctor_home.html' , context)

@login_required
@doctor_required
def doc_confirm_appointment(request,pk):
    if request.method == 'POST':
        appointment_data = Appointment.objects.get(id=pk)
        appointment_data.meeting_link = request.POST['meet']
        appointment_data.save()
        return redirect('success_appointment_doc')
    return render(request, 'doc_confirm_appointment.html')

@login_required
@doctor_required
def confirmed_appointments(request):
    my_appointments=Appointment.objects.filter(doctor=request.user, prescription="").exclude(meeting_link="no")
    # print(f"username: {request.user.username}" )
    # for i in my_appointments:
    #     print(i.patient.username)
    context={
        "appointments" : my_appointments
    }
    return render(request, 'confirmed_appointment.html',context)




def prescription_page(request,pk):

    my_appointment = Appointment.objects.get(id=pk)
    #print()
    doctor_details = Doctor.objects.get(user=my_appointment.doctor)

    context={
        "appointment" : my_appointment,
        "doctor" : doctor_details
    }   

    if request.method == 'POST':
        
        age = request.POST['patient_age']
        prescrip= request.POST['prescription_details']
        
        my_appointment.prescription = f"Patient Name: {my_appointment.patient.username}\nAge: {age}\n\nMedicines:\n{prescrip}"
        my_appointment.save()

        subject = 'MedVantage - Medical Document'
        message = final_temp
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = ['redwanalirafi@gmail.com']

        
        # Create the email
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list,
        )

        email.content_subtype = 'html' 

        # Define the content for the PDF
        yoyo = "Your document content goes here"

        # Create a BytesIO buffer to hold the PDF data
        buffer = BytesIO()

        # Create a canvas object to draw on
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Draw the string content on the PDF
        c.drawString(72, height - 72, yoyo)  # Adjust coordinates as needed
        c.showPage()
        c.save()

        pdf_data = buffer.getvalue()
        buffer.close()
        # Attach the PDF
        email.attach('document.pdf', pdf_data, 'application/pdf')

        try:
            # send_mail(subject, message, from_email, recipient_list)

            # Send the email
            email.send()
            return HttpResponse('Email sent successfully!')
        except Exception as e:
            return HttpResponse(f'An error occurred: {e}')
    

    return render(request, 'start_appointment.html', context)