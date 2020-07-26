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
    
    # response html for employee and manager   
    template_response_employee = 'registration.html'
    template_reponse_manager = 'approval.html'
    
    username = request.POST.get('uname')
    managerDetails = Employee.objects.filter(employeeID=username).values_list('mgrID', 'mgrName')
    managerID = managerDetails[0][0]
    
    if managerID == "NA":
        # IF there is no managerID that means he/she is a manager.
        pendingApproval = Request.objects.filter(managerID=username).values_list('employeeID', 'username', 'date', 'zone', 'purpose', 'status')
        return render(request, template_reponse_manager, {'pendingApproval': pendingApproval, 'length_records': len(pendingApproval)})
    else:
        return render(request, template_response_employee)


@login_required()
@csrf_exempt
def updateValidRequest(request):
    
    #Response to be sent to this
    template_response = 'acknowledge.html'
    
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
    
    managerDetails = Employee.objects.filter(employeeID=id).values_list('mgrID', 'mgrName')
    managerID = managerDetails[0][0]
    managerName = managerDetails[0][1]
    
    record = Request(employeeID=id, username=username, managerID=managerID, managerName=managerName, date=today, zone=zone, purpose=purpose, status=status)
    record.save()
    
    return render(request, template_response, {'employeeID': id, 'username': username, 'managerID': managerID, 'managerName': managerName, 'date': today, 'zone': zone, 'purpose': purpose, 'status': status})  