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
from django.db.models import Q

from .forms import DateForm
from .models import Employee
from .models import Request
from .models import QuotaStore
from .models import QuotaRequest

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
                quota = QuotaStore.objects.filter(mgrID=username, date=date).\
                    values_list('quotaAmount')[0][0]
                total_emp = len(emps)
                approve_emps = len(set([k[0] for k in approved_reqs]))

                if approve_emps + 1 > quota:
                    return HttpResponse({"failed": "yes"})
            else:
                emps = Employee.objects.filter()
                approved_reqs = Request.objects.filter(status=APPROVED,
                                                       date=date). \
                    values_list('employeeID')
                total_emp = len(emps)
                approve_emps = len(set([k[0] for k in approved_reqs]))
                if ((approve_emps + 1) * 100) > (total_emp * limit):
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
            mgrID = request.user.username
            pending_reqs = Request.objects.filter(
                managerID=mgrID, date=date).values_list(
                'id', 'employeeID', 'username',
                'date', 'zone', 'purpose', 'status')
            emps = Employee.objects.filter(mgrID=username)
            approved_reqs = Request.objects.filter(status=APPROVED,
                                                   date=date, managerID=username
                                                   ).values_list(
                                                    'employeeID'
                                                    )
            date = datetime.date.today()
            dates = [date]
            for i in range(5):
                date = get_next_working_day(date)
                dates.append(date)

            others_reqs = QuotaRequest.objects.filter(~Q(reqMgrID=mgrID),
                                                      date__in=dates)
        else:        
            emps = Employee.objects.filter()
            approved_reqs = Request.objects.filter(status=APPROVED, date=date).\
                values_list('employeeID')

            pending_reqs = Request.objects.filter(date=date).values_list(
                'id', 'employeeID', 'username',
                'date', 'zone', 'purpose', 'status')
            template = hr_dashboard_template
            others_reqs = []

        total_emp = len(emps)
        approve_emps = len(set([k[0] for k in approved_reqs]))

        return render(request, template,
                      {'pendingApproval': pending_reqs,
                       'length_records': len(pending_reqs),
                       'date_form': date_form,
                       'reject_emps': total_emp-approve_emps,
                       'approve_emps': approve_emps,
                       'others_reqs': others_reqs,
                       'limit': limit,
                       'fullname': name})
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
    defaults = {
        'quotaAmount': quotaAmount,
        'status': status
    }

    QuotaRequest.objects.update_or_create(reqMgrID=reqMgrID,
                                          date=date,
                                          defaults=defaults,
                                          )
    
    return render(request, quota_request_template, {'reqMgrID': reqMgrID,
                                                    'date': date,
                                                    'quotaAmount': quotaAmount,
                                                    'status': PENDING})


@login_required()
@csrf_exempt
def donatequota(request):
    def _get_parsed_date(date_string):
        try:
            return datetime.datetime.strptime(date_string, "%B %d, %Y")
        except ValueError:
            if "." in date_string:
                return datetime.datetime.strptime(date_string, "%b. %d, %Y")
            else:
                return datetime.datetime.strptime(date_string, "%b %d, %Y")

    donated_manager_template = "donatedQuota.html"
    # Donate quota to managers who have requested for resources
    donorMgrID = request.user.username
    status = APPROVED
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    record = eval(body['data'])
    reqQuotaAmount = int(eval(record[3]))
    
    # Get Date, Request Manager ID to update the corresponding entry
    reqMgrID = record[1]
    date = _get_parsed_date(record[2])

    
    # Substract donated quota from the donorMgr quota
    totalQuota = QuotaStore.objects.filter(mgrID=donorMgrID, date=date).values_list(
        "quotaAmount"
    )[0][0]
    approvedRequests = Request.objects.filter(managerID=donorMgrID, date=date, status=APPROVED).values_list(
        "status"
    )
    newDonarQuota = totalQuota - len(approvedRequests) - reqQuotaAmount
    if newDonarQuota >= 0:
        # Reduce donor quota
        QuotaStore.objects.filter(mgrID=donorMgrID, date=date).update(quotaAmount=newDonarQuota)
        
        # Add Quota to reqMgr quota
        requestorQuota = QuotaStore.objects.filter(mgrID=reqMgrID, date=date).values_list(
            "quotaAmount"
        )[0][0]

        newRequestorQuota = requestorQuota + reqQuotaAmount
        QuotaStore.objects.filter(mgrID=reqMgrID, date=date).update(quotaAmount=newRequestorQuota)
            
        QuotaRequest.objects.filter(reqMgrID=reqMgrID, date=date).\
            update(donorMgrID=donorMgrID, status=status)
       
        return render(request, donated_manager_template, 
                      {'donorMgrID': donorMgrID,
                       'reqMgrID': reqMgrID,
                       'donatedQuota': reqQuotaAmount,
                       'newDonarQuota': newDonarQuota,
                       'date': date}
                      )
    else:
        return HttpResponse({"failed": "yes"})
    
    
@login_required()
@csrf_exempt
def quotastore(request):
    # Fetch quota report of the specific manager
    mgrID = request.user.username
    date = datetime.date.today()
    dates = [date]
    for i in range(5):
        date = get_next_working_day(date)
        dates.append(date)

    quota_list = QuotaStore.objects.filter(mgrID=mgrID, date__in=dates)
    quota_reqs = QuotaRequest.objects.filter(reqMgrID=mgrID, date__in=dates)
    others_reqs = QuotaRequest.objects.filter(~Q(reqMgrID=mgrID),
                                              date__in=dates)

    return render(request, "mgr_quota.html", {'quota_list': quota_list,
                                              'date_form': DateForm(),
                                              'quota_reqs': quota_reqs,
                                              'others_reqs': others_reqs
                                              })


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
        quotaAmount = (empCount*limit)/100
        # Populate QuotaStore for next 5 days
        date = datetime.date.today()
        for i in range(5):
            defaults = {'quotaAmount': quotaAmount}
            QuotaStore.objects.update_or_create(mgrID=managerID, date=date,
                                                defaults=defaults
                                                )
            date = get_next_working_day(date)


def reset_quota_and_requests():
    QuotaRequest.objects.filter().update(donorMgrID="", status=PENDING)
    Request.objects.filter().update(status=PENDING)


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


class QuotaRequestView(DetailView):
    model = QuotaRequest
    template_name = "quotarequestdetail.html"

    def get(self, request, *args, **kwargs):
        record = get_object_or_404(QuotaRequest, pk=kwargs['pk'])
        context = {'record': record}
        return render(request, 'quotarequestdetail.html', context)


def get_next_working_day(date):
    for i in range(1,5):
        delta = datetime.timedelta(days=i)
        next_day = date + delta
        if next_day.weekday() in range(5):
            return next_day
