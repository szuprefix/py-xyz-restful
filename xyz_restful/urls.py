from django.urls import path
from xyz_util.views import csrf_token

urlpatterns = [
    path('csrf_token/', csrf_token, name='csrf_token')
]

