from django.contrib import admin
from api.models import Department, Job, HiredEmployee

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'department',)
    search_fields = ('id', 'department',)
    ordering = ('id',)

@admin.register(HiredEmployee)
class HiredEmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
    ordering = ('-id',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'job')
    search_fields = ('id', 'job')
    ordering = ('id',)