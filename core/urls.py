from django.contrib import admin
from django.urls import path
from . import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('',views.index,name="home"),
    path('login/',views.user_login,name="login"),
    path('register/',views.user_register,name="register"),
    path('complete_signup/',views.complete_profile,name="complete_profile"),
    path('logout/',views.user_logout,name="logout"),
    path('dashboard/',views.user_dashboard,name="dashboard"),
    path('dashboard-doctor/',views.doctor_home,name="doctor_home"),
    path('dashboard-doctor/confirm/<int:pk>',views.doc_confirm_appointment,name="doc_confirm_appointment"),
    path('dashboard-doctor/confirm/success',views.success_appointment_doc,name="success_appointment_doc"),
    path('dashboard-doctor/confirmed-appointments',views.confirmed_appointments,name="confirmed_appointments"),
    path('dashboard-doctor/prescription/<int:pk>',views.prescription_page,name="prescription_page"),
    path('dashboard-doctor/finish',views.finish_appointment,name="finish_appointment"),

    

    path('dashboard/doctors/',views.see_doctors,name="see_doctors"),
    path('dashboard/create-appointment/<str:pk>',views.create_appointment,name="create_appointment"),
    path('dashboard/appointment/success',views.success_appointment,name="success_appointment"),
    


    path('admin-panel/',views.admin_panel,name="admin_panel"),
    path('admin-panel/manage-users',views.admin_manage_users,name="admin_manage_users"),
    path('admin-panel/add-doctor',views.add_doctor,name="add-doctor"),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
