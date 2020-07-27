from django.contrib import admin

# Register your models here.
from django.contrib import admin
from core.models import Request
from core.models import Employee


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employeeID', 'employeeName', 'mgrID', 'mgrName', 'role']


class RequestAdmin(admin.ModelAdmin):
    list_display = ['employeeID', 'username', 'managerID', 'managerName',
                    'date', 'status']


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Request, RequestAdmin)

