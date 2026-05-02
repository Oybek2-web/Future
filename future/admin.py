from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Branch, Service, Queue

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'phone', 'email', 'is_staff', 'date_joined']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Qo\'shimcha', {'fields': ('phone',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Qo\'shimcha', {'fields': ('phone',)}),
    )

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'address']
    search_fields = ['name', 'address']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'duration']
    list_filter = ['branch']
    search_fields = ['name']

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ['number', 'user', 'service', 'branch', 'status', 'created_at']
    list_filter = ['status', 'branch', 'service', 'created_at']
    search_fields = ['user__username', 'user__phone']
    readonly_fields = ['number', 'created_at', 'started_at', 'finished_at']