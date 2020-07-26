# -*- coding: utf-8 -*-

import datetime

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from IMPLEMENTATION.forms import SignUpForm
from IMPLEMENTATION.models import Employee
from IMPLEMENTATION.models import Request
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
#from django.contrib.auth.forms import UserCreationForm


class MainView(TemplateView):

    @csrf_exempt
    @method_decorator(login_required)
    def get(self, request):
        
        #Get time in required format
        fmt = '%Y%m%d'
        today = datetime.datetime.now().strftime(fmt)
        

@login_required()
@csrf_exempt
def registration(request):
       
    template_response = 'registration.html'
    return render(request, template_response)


@login_required()
@csrf_exempt
def updateValidRequest(request):
    
    #Update Employee Table with the record.
    id = request.POST.get('employeeid')
    username = request.POST.get('FullName')
    purpose = request.POST.get('purpose')
    area = request.POST.get('area')
    zone = request.POST.get('zone')
    status="Pending Approval"
    # Date
    fmt = '%Y-%m-%d'
    today = datetime.datetime.now().strftime(fmt)
    
    record = Request(employeeID=id, mgrID=123, date=today, zone=zone, purpose=purpose, status=status)
    record.save()