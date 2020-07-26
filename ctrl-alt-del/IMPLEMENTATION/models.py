from __future__ import unicode_literals
from django.db import models

class Employee(models.Model):
    employeeID = models.CharField(max_length=255) # fkey: Employee with role empl
    mgrID = models.CharField(max_length=255) # fkey: Employee with role mgr
    
class Request(models.Model):
    id = models.AutoField(primary_key=True) #pkey
    employeeID = models.CharField(max_length=10) # fkey: Employee with role empl
    mgrID = models.CharField(max_length=255) # fkey: Employee with role mgr
    date = models.DateField()
    zone = models.CharField(max_length=255)
    purpose = models.TextField()
    status = models.CharField(max_length=255)
