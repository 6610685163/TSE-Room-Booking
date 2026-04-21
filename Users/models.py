from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class UserProfile(models.Model):
    """
    Extended user profile to store additional information and role assignment
    Requirement: FR-AUTH-05 - Role (Lecturer / Admin) assignment
    """
    ROLE_CHOICES = [
        ('lecturer', _('อาจารย์')),  # Lecturer
        ('admin', _('เจ้าหน้าที่')),    # Admin/Staff
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tu_username = models.CharField(max_length=100, unique=True)  # TU REST API username
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='lecturer')
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('ผู้ใช้งาน')
        verbose_name_plural = _('ผู้ใช้งาน')
    
    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_lecturer(self):
        return self.role == 'lecturer'


class Room(models.Model):
    """
    Room model for the 5 rooms mentioned in SRS
    Section 2.3: ข้อมูลห้อง (Room Information)
    """
    ROOM_TYPE_CHOICES = [
        ('meeting', _('ห้องประชุม')),      # Meeting room
        ('classroom', _('ห้องเรียน')),      # Classroom
    ]
    
    room_code = models.CharField(max_length=20, unique=True)      # 406-3, 406-5, etc.
    room_name = models.CharField(max_length=100)                   # Name in Thai
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    capacity = models.IntegerField()                               # Number of seats
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('ห้อง')
        verbose_name_plural = _('ห้อง')
        ordering = ['room_code']
    
    def __str__(self):
        return f"{self.room_code} - {self.room_name}"
