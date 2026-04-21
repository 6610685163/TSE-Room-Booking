from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import UserProfile, Room


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile
    Requirement: FR-AUTH-05 - Role assignment
    """
    list_display = ('full_name', 'tu_username', 'role', 'email', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('tu_username', 'full_name', 'email')
    readonly_fields = ('tu_username', 'created_at', 'updated_at')
    fieldsets = (
        (_('ข้อมูลพื้นฐาน'), {
            'fields': ('user', 'tu_username', 'full_name', 'email')
        }),
        (_('บทบาท'), {
            'fields': ('role',)
        }),
        (_('สถานะ'), {
            'fields': ('is_active',)
        }),
        (_('วันที่'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            # Log role change
            import logging
            logger = logging.getLogger('Users.admin')
            logger.info(
                f"Admin {request.user.username} changed {obj.tu_username} role to {obj.role}"
            )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """
    Admin interface for Room management
    Requirement: FR-ADM-01 - Room management
    """
    list_display = ('room_code', 'room_name', 'room_type', 'capacity', 'is_active')
    list_filter = ('room_type', 'is_active')
    search_fields = ('room_code', 'room_name')
    fieldsets = (
        (_('ข้อมูลห้อง'), {
            'fields': ('room_code', 'room_name', 'room_type', 'capacity')
        }),
        (_('รายละเอียด'), {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        (_('สถานะ'), {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

