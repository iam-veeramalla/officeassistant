# -*- coding: utf-8 -*-

import datetime
import json

from datetime import timedelta
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.views.generic import ListView, DetailView
from .forms import SignUpForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
#from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .forms import DateForm
from .models import Employee
from .models import Request

# Request status
PENDING = "Pending Approval"
APPROVED = "Approved"
REJECTED = "Rejected"

# Employee roles
ENGG = "Engineer"
MGR = "Manager"
HR = "HR"

limit = 50

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
    date_form = DateForm()

    username = request.user.username
    details = Employee.objects.filter(employeeID=username).values_list(
        "employeeName")
    fullname = details[0][0]
    return render(request, template_response_employee, {'employeeID': username,
                                                        'fullname': fullname,
                                                        'date_form': date_form})


@login_required()
@csrf_exempt
def createRequest(request):
    
    #Response to be sent to this
    template_response = 'acknowledge.html'
    
    #Update Employee Table with the record.
    empID = request.user.username
    purpose = request.POST.get('purpose')
    area = request.POST.get('area')
    zone = request.POST.get('zone')
    status=PENDING
    # Date
    date = request.POST.get('date')

    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    
    managerDetails = Employee.objects.filter(employeeID=empID).values_list('mgrID', 'mgrName', 'employeeName')
    managerID = managerDetails[0][0]
    managerName = managerDetails[0][1]
    username = managerDetails[0][2]

    # try:
    #     records = Request.objects.filter(date=date, employeeID=empID)
    #     record = records[0]
    # except:
    #     record = Request(employeeID=empID, username=username, managerID=managerID, managerName=managerName, date=date, zone=zone, purpose=purpose, status=status)
    #     record.save()

    default_rec = {"employeeID": empID, "username": username,
                   "managerID": managerID, "managerName": managerName,
                   "date": date, "zone": zone, "purpose": purpose,
                   "status": status}
    record, created = Request.objects.update_or_create(date=date,
                                                       employeeID=empID,
                                                       defaults=default_rec)
    
    return render(request, template_response, {'id': record.id, 'employeeID': empID, 'username': username, 'managerID': managerID, 'managerName': managerName, 'date': date, 'zone': zone, 'purpose': purpose, 'status': status})


@login_required()
@csrf_exempt
def updateRequest(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    reqid = eval(body['data'])[0]
    req = Request.objects.filter(id=reqid)
    action = body['action']
    status = PENDING
    if action == 'approve':
        username = request.user.username
        details = Employee.objects.filter(employeeID=username).values_list(
            "employeeName",
            "role"
        )
        role = details[0][1]

        if role in [MGR, HR]:
            if request.method == "GET":
                date = datetime.date.today()
            else:
                try:
                    date = request.POST.get('date')
                    date = datetime.datetime.strptime(date, '%Y-%m-%d')
                except:
                    date = eval(body["data"])[3]
                    date = datetime.datetime.strftime(date, '%Y-%m-%d')

            if role == MGR:
                emps = Employee.objects.filter(mgrID=username)
                approved_reqs = Request.objects.filter(status=APPROVED,
                                                       date=date,
                                                       managerID=username
                                                       ).values_list(
                    'employeeID'
                )
            else:
                emps = Employee.objects.filter()
                approved_reqs = Request.objects.filter(status=APPROVED,
                                                       date=date). \
                    values_list('employeeID')


            total_emp = len(emps)
            approve_emps = len(set([k[0] for k in approved_reqs]))
            global limit
            if ((approve_emps+1)*100) > (total_emp*limit):
                return HttpResponse({"failed": "yes"})

        status = APPROVED
    if action == 'reject':
        status = REJECTED
    
    #Change this
    #emailId = Employee.objects.filter(employeeID=req.employeeID).values_list(
    #    "emaliID",
    #)[0][0]
    emailId = "subbuv226@gmail.com"

    try:
        import thread
        thread.start_new_thread(send_mail, (
            'F5 Request Pass Update',
            'Your Request is ' + status,
            'abhishek.veeramalla@gmail.com',
            [emailId],
            # fail_silently = False,
        ))
    except:
        pass
        
    req.update(status=status)

    return HttpResponse({"success": "yes"})


@login_required()
@csrf_exempt
def dashboard(request):
    # response html for employee and manager
    emp_dashboard_template = "emp_home.html"
    mgr_dashboard_template = 'mgr_home.html'
    hr_dashboard_template = "hr_home.html"

    username = request.user.username
    details = Employee.objects.filter(employeeID=username).values_list(
        "employeeName",
        "role"
    )
    name = details[0][0]
    role = details[0][1]

    if role in [MGR, HR]:
        if request.method == "GET":
            date = datetime.date.today()
        else:
            date = request.POST.get('date')
            date = datetime.datetime.strptime(date, '%Y-%m-%d')

        date_form = DateForm(initial={'date': date})
        template = mgr_dashboard_template
        if role == MGR:
            emps = Employee.objects.filter(mgrID=username)
            approved_reqs = Request.objects.filter(status=APPROVED,
                                                   date=date, managerID=username
                                                   ).values_list(
                                                    'employeeID'
                                                    )
            pending_reqs = Request.objects.filter(
                managerID=username, date=date).values_list(
                'id', 'employeeID', 'username',
                'date', 'zone', 'purpose', 'status')
        else:        
            emps = Employee.objects.filter()
            approved_reqs = Request.objects.filter(status=APPROVED, date=date).\
                values_list('employeeID')

            pending_reqs = Request.objects.filter(date=date).values_list(
                'id', 'employeeID', 'username',
                'date', 'zone', 'purpose', 'status')
            template = hr_dashboard_template

        total_emp = len(emps)
        approve_emps = len(set([k[0] for k in approved_reqs]))

        return render(request, template,
                      {'pendingApproval': pending_reqs,
                       'length_records': len(pending_reqs),
                       'date_form': date_form,
                       'reject_emps': total_emp-approve_emps,
                       'approve_emps': approve_emps,
                       'limit': limit})
    else:
        return render(request, emp_dashboard_template, {'fullname': name})
    
@login_required()
@csrf_exempt
def quotarequest(request):
    
    quota_request_template = "quotarequest.html"
    # Get Date, Request Manager ID, Quota Requested
    date = request.POST.get('date')
    reqMgrID = request.user.username
    quotaAmount = request.POST.get('quotaAmount')
    status = PENDING
    
    # Save quotarequest with requested manager details and date of request
    quotastore = QuotaRequest.objects.update_or_create(reqMgrID=reqMgrID, 
                                                      quotaAmount=quotaAmount, 
                                                      date=date, 
                                                      status=status
                                                      )
    
    return render(request, quota_request_template, 
                  {'reqMgrID': reqMgrID},
                  {'date': date},
                  {'quotaAmount': quotaAmount},
                  {'status': PENDING},
                )    

@login_required()
@csrf_exempt
def donatequota(request):
    
    donated_manager_template = "donatedQuota.html"
    # Donate quota to managers who have requested for resources
    donorMgrID = request.user.username
    status = APPROVED 
    reqQuotaAmount = request.POST.get('quotaAmount') 
    
    # Get Date, Request Manager ID to update the corresponding entry
    reqMgrID = request.POST.get('reqMgrID')
    date = request.POST.get('date')
    
    # Substract donated quota from the donorMgr quota
    totalQuota = QuotaStore.objects.filter(mgrID=donorMgrID, date=date).values_list(
        "quotaAmount"
    )
    approvedRequests = Request.objects.filter(mgrID=donorMgrID, date=date).values_list(
        "Approved"
    )  
    newDonarQuota = totalQuota - len(approvedRequests) - reqQuotaAmount
    if newDonarQuota >= 0:
        quotastore = QuotaStore.objects.filter(mgrID=donorMgrID, date=date).\
            update(quotaAmount=newDonarQuota)
        
        # Add Quota to reqMgr quota
        totalQuota = QuotaStore.objects.filter(mgrID=reqMgrID, date=date).values_list(
            "quotaAmount"
        )  
        approvedRequests = Request.objects.filter(mgrID=reqMgrID, date=date).values_list(
            "Approved"
        ) 
        newRequestorQuota = availableQuota + reqQuotaAmount - approvedRequests
        quotastore = QuotaStore.objects.filter(mgrID=reqMgrID, date=date).\
            update(quotaAmount=newRequestorQuota)
            
        QuotaRequest.objects.filter(reqMgrID=reqMgrID, date=date).\
            update(donorMgrID=donorMgrID, status=status)
       
        return render(request, donated_manager_template, 
                      {'donorMgrID': donorMgrID},
                      {'reqMgrID': reqMgrID},
                      {'donatedQuota': reqQuotaAmount},
                      {'newDonarQuota': newDonarQuota},
                      {'date': date}
                    )
    else:
        return HttpResponse({"You donot have enough quota to approve this request"})
    
    
@login_required()
@csrf_exempt
def quotastore(request):
    
    # Fetch quota report of the specific manager
    mgrID = request.user.username
    dates = datetime.date.today()+timedelta(days=5)
    quotastore = QuotaStore.objects.filter(mgrID=mgrID, date=dates).values_list(
        "mgrID",
        "date",
        "quotaAmount"
    )  
    return render(request, QUOTA_STORE_HTML, {'quotastore': quotastore})

@login_required()
@csrf_exempt
def set_limit(request):
    global limit
    limit = int(request.POST.get('limit'))
    populate_quota_store()
    return redirect("/dashboard")

def populate_quota_store():
    allManagers = Employee.objects.filter(role=MGR).values_list('employeeID')
    for manager in allManagers:
        managerID = manager[0]
        # Get number of employees under this manager 
        # based on the percentage calculate it
        empOfMgr = Employee.objects.filter(mgrID=managerID).values_list('employeeID')
        empCount = len(empOfMgr)
        quotaAmount = float(empCount*limit)/100
        # Populate QuotaStore for next 5 days
        delta = datetime.timedelta(days=1)
        for i in range(5):
            # Use update_or_create
            quotastore = QuotaStore.objects.update_or_create(mgrID=managerID, 
                                                             date=date, 
                                                             quotaAmount=quotaAmount
                                                            )
            quotastore.save()
            date += delta

class RequestsView(ListView):
    model = Request
    # paginate_by = 10
    template_name = "requests.html"

    def get_queryset(self):
        return Request.objects.filter(employeeID=self.request.user.username)

class RequestView(DetailView):
    model = Request
    template_name = "requestdetail.html"

    def get(self, request, *args, **kwargs):
        record = get_object_or_404(Request, pk=kwargs['pk'])
        context = {'record': record}
        return render(request, 'requestdetail.html', context)

