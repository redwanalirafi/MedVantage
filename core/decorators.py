from django.http import HttpResponseForbidden
from functools import wraps
from django.contrib.auth.decorators import login_required
from .models import Doctor,User


def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            Doctor.objects.get(user=request.user)
            return view_func(request, *args, **kwargs)
        except Doctor.DoesNotExist:
            return HttpResponseForbidden("You must be a doctor to access this page.")
    return _wrapped_view

def assistant_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            Doctor.objects.get(assistant=request.user)
            return view_func(request, *args, **kwargs)
        except Doctor.DoesNotExist:
            return HttpResponseForbidden("You must be a assistant to access this page.")
    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You must be an admin to access this page.")
    
    return _wrapped_view