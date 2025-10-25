from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib import messages
import base64
from .models import CaptureMetadata
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
from ultralytics import YOLO
import json
from .models import CustomUser
import random

# ---------------- Detection Models ----------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
yolo_model = YOLO("yolov8n.pt")  # Ensure this weights file exists

# ---------------- HOME ----------------
def home(request):
    return render(request, 'home.html')

# ---------------- SIGN UP ----------------
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, "signup.html", {"username": username, "email": email})

        # Generate 6-digit numeric password
        numeric_password = str(random.randint(100000, 999999))
        user = CustomUser.objects.create_user(username=username, email=email, password=numeric_password)

        messages.success(request, f"Account created! Your password: {numeric_password}")
        return redirect("login")

    return render(request, "signup.html")


# ----------------  LOGIN ----------------

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('detector')  # Redirect to AI detector page
        else:
            return render(request, 'login.html', {'error': 'Invalid email or password'})

    return render(request, 'login.html')


# ---------------- LOGOUT ----------------
def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


# ---------------- DETECTOR PAGE ----------------
def detector(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'detector.html')


# ---------------- IMAGE CAPTURE ----------------
@csrf_exempt
def capture_image(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    try:
        data = json.loads(request.body).get('image')
        if not data:
            return JsonResponse({'error': 'No image provided'}, status=400)

        header, encoded = data.split(",", 1)
        img_data = base64.b64decode(encoded)

        # Face detection
        img = Image.open(BytesIO(img_data))
        open_cv_image = np.array(img.convert('RGB'))
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        num_faces = len(faces)

        # Object detection using YOLO
        results = yolo_model.predict(open_cv_image, verbose=False)
        num_objects = len(results[0].boxes)

        obj = CaptureMetadata.objects.create(
            media_type='image',
            image_data=img_data,
            detected_faces=num_faces,
            detected_objects=num_objects
        )

        return JsonResponse({'success': True, 'id': obj.id})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ---------------- VIDEO CAPTURE ----------------
@csrf_exempt
def capture_video(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        video_file = request.FILES.get('video')
        if not video_file:
            return JsonResponse({'error': 'No video file'}, status=400)

        video_data = video_file.read()
        obj = CaptureMetadata.objects.create(
            media_type='video',
            video_data=video_data
        )

        return JsonResponse({'success': True, 'id': obj.id})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ---------------- LIST MEDIA ----------------
def list_media(request):
    photos = []
    videos = []

    for obj in CaptureMetadata.objects.all().order_by('-timestamp'):
        if obj.media_type == 'image' and obj.image_data:
            photos.append({
                'id': obj.id,
                'url': 'data:image/png;base64,' + base64.b64encode(obj.image_data).decode(),
                'faces': obj.detected_faces,
                'objects': obj.detected_objects,
                'timestamp': obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        elif obj.media_type == 'video' and obj.video_data:
            videos.append({
                'id': obj.id,
                'url': f'/media/video/{obj.id}/',
                'timestamp': obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })

    return JsonResponse({'photos': photos, 'videos': videos})


# ---------------- SERVE VIDEO ----------------
def serve_video(request, media_id):
    try:
        obj = CaptureMetadata.objects.get(id=media_id, media_type='video')
        return HttpResponse(obj.video_data, content_type='video/webm')
    except CaptureMetadata.DoesNotExist:
        return HttpResponse(status=404)


# ---------------- DELETE MEDIA ----------------
@csrf_exempt
def delete_media(request, media_id):
    try:
        obj = CaptureMetadata.objects.get(id=media_id)
        obj.delete()
        return JsonResponse({'success': True})
    except CaptureMetadata.DoesNotExist:
        return JsonResponse({'error': 'Media not found'}, status=404)


# ---------------- FRAME ANALYSIS (Optional) ----------------
def analyze_frame(request):
    return JsonResponse({'status': 'ok', 'message': 'Frame analyzed successfully'})
