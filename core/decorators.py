from django.http import HttpResponseForbidden
from functools import wraps
from django.contrib.auth.decorators import login_required
from .models import Doctor

# Custom decorator to check if the user is a doctor
def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            Doctor.objects.get(user=request.user)
            return view_func(request, *args, **kwargs)
        except Doctor.DoesNotExist:
            return HttpResponseForbidden("You must be a doctor to access this page.")
    return _wrapped_view
