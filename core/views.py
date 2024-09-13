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
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from reportlab.lib.units import inch



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

            return redirect('login')
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
                
                if not UserProfile.objects.filter(user=user).exists():
                    return redirect('complete_profile')
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
    if not UserProfile.objects.filter(user = request.user).exists():
        return redirect('complete_profile')
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

    user_age = UserProfile.objects.get(user__username = my_appointment.patient.username).age

    document_url = request.build_absolute_uri(my_appointment.document.url)
    context={
        "appointment" : my_appointment,
        "doctor" : doctor_details,
        "patient_age" : user_age,
        "doc_url" : document_url
    }   

    if request.method == 'POST':
        
        
        prescrip= request.POST.getlist('medications[]')
        
        my_appointment.prescription = f"Patient Name: {my_appointment.patient.first_name} {my_appointment.patient.last_name}\nAge: {user_age}\n\nMedicines:\n{prescrip}"
        my_appointment.save()

        subject = 'MedVantage - Medical Document'
        message = final_temp
        from_email = settings.DEFAULT_FROM_EMAIL

        recipient_list = [my_appointment.patient.email]
     

        
        # Create the email
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list,
        )

        email.content_subtype = 'html' 

                # Create the medicines list
        medicines_list = [Paragraph(f'{med}', getSampleStyleSheet()['Normal']) for med in prescrip]

        # Create a BytesIO buffer to hold the PDF data
        buffer = BytesIO()

        # Set up a SimpleDocTemplate for the PDF
        pdf = SimpleDocTemplate(buffer, pagesize=letter)

        # Define styles for the document
        styles = getSampleStyleSheet()

        # Custom styles for a more polished look
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.fontSize = 20
        title_style.textColor = colors.darkblue
        title_style.spaceAfter = 20
        styles = getSampleStyleSheet()
        body_style = styles['BodyText']
        body_style.fontSize = 14
        body_style.textColor = colors.black
        body_style.spaceAfter = 14
        body_text_style = styles['BodyText']
        body_text_style.fontSize = 14
        body_text_style.textColor = colors.black
        body_text_style.spaceAfter = 14

        styles.add(ParagraphStyle(name='Subheading', fontSize=16, textColor=colors.blue, spaceAfter=10))

        # Create the list of elements for the PDF
        elements = [
            Paragraph('<h2>MedVantage</h2>', styles['Title']),
            Paragraph('<h5>Online Healthcare Platform</h5>', styles['Title']),
            Spacer(1, 0.5*inch),  # Add some space before the next section
            Paragraph(f"Patient Name: {my_appointment.patient.first_name} {my_appointment.patient.last_name}", styles['BodyText']),
            Paragraph(f"Age: {user_age}", styles['BodyText']),
            Spacer(1, 0.2*inch),
            Paragraph('<strong>Medicines:</strong>', styles['BodyText']),
            ListFlowable(medicines_list, bulletType='bullet', start='circle'),  # Bullet-pointed list
        ]

        # Build the PDF content
        pdf.build(elements)

        pdf_data = buffer.getvalue()
        buffer.close()
        # Attach the PDF
        email.attach('document.pdf', pdf_data, 'application/pdf')

        try:
            # send_mail(subject, message, from_email, recipient_list)

            # Send the email
            email.send()
            return redirect('finish_appointment')
        except Exception as e:
            return HttpResponse(f'An error occurred: {e}')
    

    return render(request, 'start_appointment.html', context)


def complete_profile(request):
    if request.method == 'POST':
        f_name = request.POST.get('firstName', '').strip()  # Remove extra spaces
        l_name = request.POST.get('lastName', '').strip()
        email = request.POST.get('user_email', '').strip()
        age = request.POST.get('age', '').strip()

        # Check if all fields are filled out
        if not f_name or not l_name or not email or not age:
            # If any of the fields are empty, return an error message
            error_message = "All fields are required. Please fill out the entire form."
            return render(request, 'complete_profile2.html', {'error_message': error_message})

        # Print values for debugging
        
        user_obj = request.user  #user_obj = User.objects.get(user=request.user)
        user_obj.first_name = f_name
        user_obj.last_name = l_name
        user_obj.email=email

        user_obj.save()

        user_profile, created = UserProfile.objects.get_or_create(user=user_obj)
        user_profile.age = age
        user_profile.save()

    return render(request, 'complete_profile2.html')


def finish_appointment(request):
    return render(request, 'finish_appointment.html')