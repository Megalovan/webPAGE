# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
import json
# Create your views here.
def index(request):
    return render(request, 'index.html')
'''
def control(request):
    statue = 1
    text = "发送成功"
    ifup = request.POST.get('ifup','')
    upSpeed = request.POST.get('upSpeed','')
    ifmid = request.POST.get('ifmid','')
    midSpeed = request.POST.get('midSpeed','')
    ifbo = request.POST.get('ifbo','')
    boSpeed = request.POST.get('boSpeed','')
    print(ifup,upSpeed)
    print(ifmid,midSpeed)
    print(ifbo,boSpeed)
    data={
        'mainControl':1,
        'data':{
            'ifup':ifup,
            'upSpeed':upSpeed,
            'ifmid':ifmid,
            'midSpeed':midSpeed,
            'ifbo':ifbo,
            'boSpeed':boSpeed,
        }
    }
        data_json = json.dumps(data)
        HOST = '172.16.0.4'
        PORT = 9999
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    conn, addr = sock.accept()
        conn.send(data_json.encode())
        conn.close()
'''
