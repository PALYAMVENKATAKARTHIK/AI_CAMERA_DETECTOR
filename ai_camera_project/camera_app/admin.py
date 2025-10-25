from django.contrib import admin
from .models import CaptureMetadata

@admin.register(CaptureMetadata)
class CaptureMetadataAdmin(admin.ModelAdmin):
    list_display = ('id', 'detected_faces', 'detected_objects', 'focus_level', 'lighting_level', 'timestamp')
    readonly_fields = ('timestamp',)
    
class CustomUser(admin.ModelAdmin):
    list_display=('username','email','password_code','created_at',)
