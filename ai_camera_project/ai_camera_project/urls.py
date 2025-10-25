from django.contrib import admin
from django.urls import path, include
from camera_app import views as camera_views

urlpatterns = [
    path('admin/', admin.site.urls),                     # Django Admin Panel
    path('', camera_views.home, name='home'),            # Homepage (index page)
    path('', include('camera_app.urls')),         # API routes from camera_app
]
