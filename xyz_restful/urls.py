from django.urls import path
from xyz_util.views import csrf_token

urlpatterns = [
    path(r'^csrf_token/$', csrf_token, name='csrf_token')
]

