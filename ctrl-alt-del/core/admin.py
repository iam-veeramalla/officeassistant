from django.contrib import admin

# Register your models here.
from django.contrib import admin
from core.models import Request
from core.models import Employee

admin.site.register(Request)
admin.site.register(Employee)

