from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('camera/', views.index, name='camera'),

    # --- MEDIA API ROUTES (Frontend Integration) ---
    path('capture_image/', views.capture_image, name='capture_image'),
    path('capture_video/', views.capture_video, name='capture_video'),
    path('list_media/', views.list_media, name='list_media'),
    path('media/video/<int:media_id>/', views.serve_video, name='serve_video'),
    path('delete_media/<int:media_id>/', views.delete_media, name='delete_media'),

    # --- USER AUTH ---
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),

    # --- MAIN CAMERA PAGE ---
    path('detector/', views.detector, name='detector'),
]
