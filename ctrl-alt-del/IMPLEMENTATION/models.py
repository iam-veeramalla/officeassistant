from __future__ import unicode_literals
from django.db import models

class Employee(models.Model):
    employeeID = models.CharField(primary_key=True, max_length=10) # fkey: Employee with role empl
    employeeName = models.CharField(max_length=50)
    mgrID = models.CharField(max_length=10) # fkey: Employee with role mgr
    mgrName = models.CharField(max_length=50)
    
class Request(models.Model):
    id = models.AutoField(primary_key=True) #pkey
    employeeID = models.CharField(max_length=10) # fkey: Employee with role empl
    username = models.CharField(max_length=50)
    managerID = models.CharField(max_length=10) # fkey: Employee with role mgr
    managerName = models.CharField(max_length=255)
    date = models.DateField()
    zone = models.CharField(max_length=255)
    purpose = models.TextField()
    status = models.CharField(max_length=255)
