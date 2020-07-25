# -*- coding: utf-8 -*-

import datetime

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from IMPLEMENTATION.models import Post
from IMPLEMENTATION.models import Selection
from django.views.generic import TemplateView
from IMPLEMENTATION.forms import SignUpForm
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

    # Check if he is an Employee or Manager, If he is an Employee, Provide Registration Form. 
    #p = Selection(user=username, match1=event.match1, match2=event.match2, date=today, choice1=selection1, choice2=selection2, points=0)
    #p.save()
    return render(request, template_response)