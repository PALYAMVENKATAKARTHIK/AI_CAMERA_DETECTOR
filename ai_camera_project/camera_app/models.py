from django.db import models
import random

# -----------------------------
# Capture Metadata Model
# -----------------------------
class CaptureMetadata(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
    )

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default='image'  # Default value for existing rows
    )
    detected_faces = models.IntegerField(default=0)
    detected_objects = models.IntegerField(default=0)
    focus_level = models.FloatField(default=0.0)
    lighting_level = models.FloatField(default=0.0)
    image_data = models.BinaryField(null=True, blank=True)
    video_data = models.BinaryField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.media_type.capitalize()} | Faces: {self.detected_faces} | {self.timestamp}"


# -----------------------------
# Helper Function for Random Password
# -----------------------------
def generate_numeric_password():
    return str(random.randint(100000, 999999))  # 6-digit random password


# -----------------------------
# User Model
# -----------------------------
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random

# -----------------------------
# User Manager
# -----------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        if not password:
            # generate random numeric password
            password = str(random.randint(100000, 999999))
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # hashed password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)


# -----------------------------
# Custom User Model
# -----------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'         # login with email
    REQUIRED_FIELDS = ['username']   # this is required!

    def __str__(self):
        return self.email
