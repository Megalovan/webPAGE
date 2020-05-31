# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
import json
# Create your views here.
def index(request):
    return render(request, 'index.html')

def flowrate(request):
    #return HttpResponse(u"hhh")
    return render(request, 'flowRate.html')
