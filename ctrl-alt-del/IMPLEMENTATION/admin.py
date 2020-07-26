from django.contrib import admin

# Register your models here.
from django.contrib import admin
from IMPLEMENTATION.models import Request
from IMPLEMENTATION.models import Employee

admin.site.register(Request)
admin.site.register(Employee)

