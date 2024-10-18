import os
from django.http import HttpResponse, JsonResponse
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
from .email_template import *
from django.urls import reverse

from datetime import datetime, timedelta
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

def string_to_hex(s):
    byte_representation = s.encode('utf-8')
    hex_representation = byte_representation.hex()
    return hex_representation

def hex_to_string(hex_str):
    byte_representation = bytes.fromhex(hex_str)
    string_representation = byte_representation.decode('utf-8')
    return string_representation

def index(request):
    return render(request,"index2.html")

def user_register(request):
    if request.method == 'POST':
        print("POST")
        form = SignupForm(request.POST)
        if form.is_valid():
            print("VALID")
            form.save()
            messages.success(request, 'Registration Successfull')

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
                if user.is_staff:
                    return redirect('admin_panel')

                elif Doctor.objects.filter(user=user).exists():
                    return redirect('doctor_home')
                
                elif Doctor.objects.filter(assistant=user).exists():
                    return redirect('assistant_dashboard')
                
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
    if not UserProfile.objects.filter(user=request.user).exists():
        return redirect('complete_profile')

    doc_obj = Doctor.objects.get(user__username=pk)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, request.FILES)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.doctor = doc_obj.user
            appointment.save()
            return redirect('success_appointment')
    else:
        form = AppointmentForm()

    # Generate 30-minute time slots between 9 AM and 5 PM
    start_time = datetime.strptime("09:00", "%H:%M")
    end_time = datetime.strptime("17:00", "%H:%M")
    slots = []
    while start_time < end_time:
        slots.append(start_time.strftime("%H:%M"))
        start_time += timedelta(minutes=30)

    
    selected_date = request.POST.get('date') 

    print(f"{selected_date} SELECTED")

    available_slots = slots
    if selected_date:
       
        selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()

       
        booked_slots = Appointment.objects.filter(doctor=doc_obj.user, date=selected_date_obj).values_list('time_slot', flat=True)
        formated_booked_slots = []

        for i in booked_slots:
            formated_booked_slots.append(i.strftime("%H:%M"))
            #print(i)

       
        available_slots = [slot for slot in slots if slot not in formated_booked_slots]


    return render(request, 'appointment.html', {
        'form': form,
        'user': request.user,
        'doc': doc_obj,
        'available_slots': available_slots,
        'selected_date': selected_date
    })



@login_required
def success_appointment(request):
    return render(request,"success_appointment.html")


@login_required
def success_appointment_doc(request):
    return render(request,"success_appointment_doc.html")


@admin_required
def admin_panel(request):
    return render(request, 'base_admin.html')


@admin_required
def admin_manage_users(request):
    obj= User.objects.all()

    context={
        "tatal_users" : obj.count(),
        "data" : obj
    }
    return render(request, 'admin_manage_users.html' ,context=context)


def get_usernames(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(username__icontains=query)[:5]
        data = [{'username': user.username} for user in users]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


@admin_required
def add_doctor(request):
    if request.method == 'POST':
        user_id = request.POST.get('username')  
        designation = request.POST.get('designation')  
        fee = request.POST.get('fee') 
        assistant_id = request.POST.get('assistant_id') 
        
        try:
            user = User.objects.get(username=user_id) 
            assistant = User.objects.get(id=assistant_id) if assistant_id else None 

            if Doctor.objects.filter(user=user).exists():
                return redirect('doc_add_success')
           
            doctor = Doctor.objects.create(
                user=user,
                designation=designation,
                fee=fee,
                assistant=assistant  # Optional field
            )
            
            
            return redirect('doc_add_success') 
        except User.DoesNotExist:
             return HttpResponse(f'An error occurred: Username not found')

    return render(request, 'add_doctor.html')  # Render a form for the doctor

    #return render(request, 'add_doctor.html' ,context={'form' : form})


def doc_add_success(request):

    return render(request, "doc_add_success.html")


@admin_required
def delete_doctor(request):
    obj= Doctor.objects.all()

    context={
        "tatal_users" : obj.count(),
        "data" : obj
    }
    print(obj.first().designation)
    return render(request, 'admin_manage_doctor.html' ,context=context)
 
@admin_required
def admin_remove_user(request,pk):
    user_obj = User.objects.get(id=pk)
    user_obj.delete()

    obj= User.objects.all()

    context={
        "tatal_users" : obj.count(),
        "data" : obj
    }

    return redirect('admin_manage_users')

@admin_required
def admin_remove_doc(request,pk):
    user_obj = Doctor.objects.get(id=pk)
    user_obj.delete()

    obj= User.objects.all()

    context={
        "tatal_users" : obj.count(),
        "data" : obj
    }

    return redirect('delete-doctor')

@admin_required
def make_admin(request,pk):
    user_obj = User.objects.get(id=pk)
    user_obj.is_staff=True
    user_obj.save()

    obj= User.objects.all()

    context={
        "tatal_users" : obj.count(),
        "data" : obj
    }

    return redirect('admin_manage_users')

@admin_required
def user_search(request):
    query = request.GET.get('username', '')
    if query:
        users = User.objects.filter(username__icontains=query)  # Filter users by username
    else:
        users = User.objects.all()  # Show all users if no search query

    total_users = users.count()  # Count the total number of users after filtering
    context = {
        'data': users,
        'total_users': total_users,
    }
    return render(request, 'admin_manage_users.html', context)


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

    doc_obj = Doctor.objects.get(user=request.user.id)
    if request.method == 'POST':
        appointment_data = Appointment.objects.get(id=pk)
        appointment_data.meeting_link = request.POST['meet']
        appointment_data.fee= doc_obj.fee
        appointment_data.save()

        subject = 'MedVantage - Appointment Booked'
        message = book1 + f"<a style='text-decoration: none; color:white' href='{request.POST['meet']}' class='btn-review'>Google Meet</a> on {appointment_data.date} " + book2 + f"Please pay: {doc_obj.fee}. Thank You."
        from_email = settings.DEFAULT_FROM_EMAIL

        recipient_list = [appointment_data.patient.email]
     

        
        # Create the email
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list,
        )

        email.content_subtype = 'html' 

        try:
            # send_mail(subject, message, from_email, recipient_list)

            # Send the email
            email.send()
            print("GG")
            return redirect('success_appointment_doc')
        except Exception as e:
            return HttpResponse(f'An error occurred: {e}')
        
    return render(request, 'doc_confirm_appointment.html', {"doc" : doc_obj})
    

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



@login_required
@doctor_required
def prescription_page(request,pk):

    my_appointment = Appointment.objects.get(id=pk)
    #print()
    doctor_details = Doctor.objects.get(user=my_appointment.doctor)

    user_age = UserProfile.objects.get(user__username = my_appointment.patient.username).age
    try:
        document_url = request.build_absolute_uri(my_appointment.document.url)
    except:
        document_url = None

    context={
        "appointment" : my_appointment,
        "doctor" : doctor_details,
        "patient_age" : user_age,
        "doc_url" : document_url
    }   

    scheme = request.scheme
    host = request.get_host()
    base_url = f"{scheme}://{host}/"

    review_url = base_url+"review/" + string_to_hex(f"{my_appointment.patient.username}:{my_appointment.id}")

   
    print(review_url)

    if request.method == 'POST':
        
        
        prescrip= request.POST.get('medication')
        
        print(prescrip)

        my_appointment.prescription = f"Patient Name: {my_appointment.patient.first_name} {my_appointment.patient.last_name}\nAge: {user_age}\n\nMedicines:\n{prescrip}"
        my_appointment.save()

        subject = 'MedVantage - Medical Document'
        message = final_temp + f"<a style='text-decoration: none; color:white' href='{review_url}' class='btn-review'>Leave a Review</a>. " + final_part2
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
            print("")
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
        return redirect('dashboard')

    return render(request, 'complete_profile2.html')


def finish_appointment(request):
    return render(request, 'finish_appointment.html')

def review(request,pk):
    hex_str = hex_to_string(pk)
    username = hex_str.split(':')[0]
    app_id = int(hex_str.split(':')[1])

    appointment_obj = Appointment.objects.get(id=app_id)

    if request.method == "POST":
        p_review = request.POST.get('p_review' , '')
        p_rating = request.POST.get('rating' , '')
        password = request.POST.get('passwords' , '')

        try:
          
            user = User.objects.get(username=username)

           
            if user.check_password(password):
                appointment_obj.review = p_review
                appointment_obj.rating = p_rating
                appointment_obj.save()
                return render(request, 'password_success.html')
            else:
                return HttpResponse('Password does not match.')
        except User.DoesNotExist:
            return HttpResponse('User not found.')

        
        
    context = {
        "username" : username 
    }

    return render(request, 'write_review.html', context)

@login_required
@doctor_required
def show_review(request):
    reviews_obj = Appointment.objects.filter(doctor=request.user).exclude(review="")

    print(reviews_obj)

    context = {
        "appointment" : reviews_obj
    }
    return render(request, 'show_review.html',context)

@login_required
@doctor_required
def profile(request):
    
    #my_appointment_obj = Appointment.objects.get(doctor=request.user)
    
    doctor_obj = Doctor.objects.get(user=request.user.id)

    print(doctor_obj.user.first_name)
    context = {
            "doc" : doctor_obj
    }
    if request.method == "POST":
        doc_fee = request.POST.get('fee' , '')
        doctor_obj.fee = doc_fee
        doctor_obj.save()
        context['error_message'] =  "Data updated successfully."
        

    

    return render(request, 'profile.html', context )


@login_required
@doctor_required
def assistant_manager(request):
    usernames = User.objects.values_list('username', flat=True)
    
    

    doctor_obj = Doctor.objects.get(user=request.user.id)
    
    context = {
        "usernames" : usernames,
        "doc" : doctor_obj
    }

    if request.method == "POST":
        assistant = request.POST.get('assistant' , '')

        if assistant == '':  # Check if the input is empty
            doctor_obj.assistant = None  # Remove the assistant
            doctor_obj.save()
            context['error_message'] = "Assistant removed successfully."

        elif User.objects.filter(username = assistant).exists():
            context['error_message'] =  "Assistant Added Successfully."
            doctor_obj.assistant = User.objects.get(username = assistant)
            doctor_obj.save()
        
        else:
            context['error_message'] =  "Username Not Found!"


    return render(request, 'assistant_manager.html', context)


@login_required
@assistant_required
def assistant_dashboard(request):
    context={

    }


    return render(request, 'home_assis.html', context)


@login_required
@assistant_required
def confirmed_appointments_assis(request):
    doc_obj = Doctor.objects.filter(assistant=request.user).first()

    my_appointments=Appointment.objects.filter(doctor=doc_obj.user,meeting_link="no")
    # print(f"username: {request.user.username}" )
    
    context={
        "appointments" : my_appointments
    }
    return render(request, 'pending_assis.html' , context)


def assis_confirm_appointment(request,pk):
    
    doc_obj = Doctor.objects.filter(assistant=request.user).first()

    
    if request.method == 'POST':
        appointment_data = Appointment.objects.get(id=pk)
        appointment_data.meeting_link = request.POST['meet']
        appointment_data.fee = doc_obj.fee
        appointment_data.save()

        subject = 'MedVantage - Appointment Booked'
        message = book1 + f"<a style='text-decoration: none; color:white' href='{request.POST['meet']}' class='btn-review'>Google Meet</a> on {appointment_data.date} " + book2 + f"Please pay: {doc_obj.fee}. Thank You."
        from_email = settings.DEFAULT_FROM_EMAIL

        recipient_list = [appointment_data.patient.email]
     

        
        # Create the email
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list,
        )

        email.content_subtype = 'html' 

        try:
            # send_mail(subject, message, from_email, recipient_list)

            # Send the email
            email.send()
            print("GG")
            return redirect('success_appointment_doc')
        except Exception as e:
            return HttpResponse(f'An error occurred: {e}')
        
    return render(request, 'doc_confirm_appointment.html', {"doc" : doc_obj})