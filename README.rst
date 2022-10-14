=================
XYZ RestFul API
=================

XYZ RestFul API provides a way to register django-rest-framework apis as easy as Django admins.

Usage Example
-------------

First, add 'xyz_restful' into django settings's INSTALLED_APPS
::

    INSTALLED_APPS = [
        ...
        'xyz_restful',
        ...
    ]

Then, register url router in project's ``"urls.py"``
::

    from xyz_restful.helper import router

    urlpatterns = [
        url(r'^admin/', admin.site.urls),
        url(r'^api/', include(router.urls)),
        ...
    ]

Then, in an app for example: comment , create a file ``"comment/apis.py"``
::

    from xyz_restful.decorators import register

    @register()
    class PostViewSet(viewsets.ModelViewSet):
        serializer_class = serializers.PostSerializer
        queryset = models.Post.objects.all()

then, full api url just like :
``http://127.0.0.1:8000/api/comment/post/``

Enjoyed!