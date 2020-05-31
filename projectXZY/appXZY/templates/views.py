# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.http import FileResponse
from django.shortcuts import render
from .forms import AddForm#引入创建的表单类
from . import models#引入创建的表单类
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.core.mail import send_mass_mail

import json
import random
import time
import datetime
import socket

def quikFiles(request):
    file=open('/quik/quikProject/app/static/links.pptx','rb')  
    response =FileResponse(file)  
    response['Content-Type']='application/octet-stream'  
    response['Content-Disposition']='attachment;filename="links.pptx"'  
    return response
def downloadFiles(request):
    file=open('/quik/quikProject/app/static/0.zip','rb')
    response =FileResponse(file)
    response['Content-Type']='application/octet-stream'
    response['Content-Disposition']='attachment;filename="0.zip"'
    return response
def fanke(request):
    return render(request, 'LJQ.html')
def flowRate(request):
    return render(request, 'flowRate.html')
def flowRateJson(request):
    return render(request,'flowRate.json',content_type="application/json")
def add(request):
    a = request.GET['a']
    b = request.GET['b']
    c = int(a)+int(b)
    return HttpResponse(str(c))
def addArticle(request):
    return render(request, 'addArticle.html')
def sendMessage(request):
    userId = request.GET['userId']
    user = models.UserInformation.objects.get(userId=userId)
    userName = user.userName
    from_email = settings.DEFAULT_FROM_EMAIL
    subject = '来自QUIK用户的积分申诉邮件'
    text_content = '这是一封重要的邮件,用户' + userName + ',对积分明细存有异议,请管理员核实最近该用户的积分增扣情况, 尽快给出回复.'
    #html_content = '<p>这是一封<strong>重要的</strong>邮件.</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, ['hitpioneerteam@163.com'])
    #msg.attach_alternative(html_content, "text/html") 
    msg.send()
    return HttpResponse("积分申诉提交成功!")
def bookJson(request):
    bookId = request.GET['bookId']
    book = models.Book.objects.get(bookId = bookId) 
    data = {
                'bookName':book.bookName,
                'bookSt':book.stateOfBook,
                'bookId':book.bookId,
		'bookUser':book.userId
           }
    return HttpResponse(json.dumps(data),content_type="application/json")
def userInformation(request):
    userId = request.GET['userId']
    user = models.UserInformation.objects.get(userId=userId)
    return HttpResponse(user.creditPoints)
def addCreditPoints(request):
    userId = request.GET['userId']
    addPoints = int(request.GET['addPoints'])
    user = models.UserInformation.objects.get(userId=userId)
    creditPointsResult = int(user.creditPoints) + addPoints
    if creditPointsResult >= 100 :
        user.creditPoints = 100
        user.save()
    else:
        user.creditPoints = creditPointsResult
        user.save()
    return HttpResponse("Add Credit Points Successfully!")
def reduceCreditPoints(request):
    userId = request.GET['userId']
    reducePoints = int(request.GET['reducePoints'])
    user = models.UserInformation.objects.get(userId=userId)
    creditPointsResult = int(user.creditPoints) - reducePoints
    if creditPointsResult <= 0 :
        user.creditPoints = 0
        user.save()
    else:
        user.creditPoints = creditPointsResult
        user.save()
    return HttpResponse("Reduce Credit Points Successfully!")
def borrowBook(request):
    bookId = request.GET['bookId']
    book = models.Book.objects.get(bookId = bookId)
    userId = request.GET['userId']
    user = models.UserInformation.objects.get(userId=userId)
    if ( book.stateOfBook == "N") and (int(user.creditPoints) >= 60):
        book.stateOfBook = "LK"
	book.userId = userId
        book.save()
	return HttpResponse("借阅书籍成功!")
    elif book.stateOfBook == "LK" :
        return HttpResponse("该书已被借阅!")
    elif (int(user.creditPoints) < 60) :
        return HttpResponse("您的积分低于60分,借阅受限!")  
    else :
        return HttpResponse("发生未知错误!")
def scanResult(request):
    bookId = request.GET['bookId']
    userId = request.GET['userId']
    book = models.Book.objects.get(bookId = bookId)
    user = models.UserInformation.objects.get(userId=userId)
   
    localTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    updateTime = book.pub_date.strftime("%Y-%m-%d %H:%M:%S")
    d1 = datetime.datetime.strptime(localTime, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(updateTime, '%Y-%m-%d %H:%M:%S')
    deltaTime = d1 - d2
    if book.stateOfBook == "N" :
        book.stateOfBook = "LK"
        book.userId = userId
        book.save()
        return HttpResponse("借阅书籍成功!")
    else :
        if book.userId == userId :
	    book.stateOfBook = "N"
            book.userId = "NULL"
            book.save()
            if deltaTime.days >= 2 :
                user.creditPoints = int(user.creditPoints) - 5
        	user.save()
        	return HttpResponse("归还书籍超时4个月,扣除部分信誉积分5分.")
    	    elif deltaTime.days >= 1 :
        	user.creditPoints = int(user.creditPoints) - 3
        	user.save()
        	return HttpResponse("归还书籍超时2个月,扣除部分信誉积分3分.")
    	    else :
        	return HttpResponse("归还书籍成功!")
	else :
	    return HttpResponse("这本书不是你的!")
def returnBook(request):
    bookId = request.GET['bookId']
    book = models.Book.objects.get(bookId = bookId)
    userId = request.GET['userId']
    user = models.UserInformation.objects.get(userId=userId)
    localTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    updateTime = time.strftime("%Y-%m-%d %H:%M:%S",book.update_time)
    d1 = datetime.datetime.strptime(localTime, '%Y-%m-%d %H:%M:%S')
    d2 = datetime.datetime.strptime(updateTime, '%Y-%m-%d %H:%M:%S')
    deltaTime = d1 - d2
    book.stateOfBook = "N"
    book.userId = "NULL"
    book.save()
    if deltaTime.days >= 120 :
        user.creditPoints = int(user.creditPoints) - 5
        user.save()
        return HttpResponse("归还书籍超时4个月,扣除部分信誉积分5分.")
    elif deltaTime.days >=60 :
	user.creditPoints = int(user.creditPoints) - 3
        user.save()
        return HttpResponse("归还书籍超时2个月,扣除部分信誉积分3分.")
    else :
        return HttpResponse("归还书籍成功!") 
def addArticleAction(request):
    title = request.POST.get('title','title')
    content = request.POST.get('content','content')
    models.Article.objects.create(title=title,content=content)
    return HttpResponse("Create Successfully!")
def addArticleAction2(request):
    title = request.GET['title']
    content = request.GET['content']
    models.Article.objects.create(title=title,content=content)
    return HttpResponse("Create Successfully!")
def addSeat(request):
    for i in range(1,13):
        if (i==3)or(i==6)or(i==9)or(i==12):
	    continue;
        for j in range(1,12):
            a = str(i);
	    b = str(j);
   	    columnId = b;
	    seatNo = a + '_' + b; 
            models.Seat.objects.create(columnId=columnId,seatNo=seatNo,st='N',userId='NULL')
        for k in range(16,26):
            a = str(i);
            b = str(k);
            columnId = b;
            seatNo = a + '_' + b;
            models.Seat.objects.create(columnId=columnId,seatNo=seatNo,st='N',userId='NULL')
    return HttpResponse("Create Successfully!")
def json2(request):
    data = {  
        'info' : {
            'username':'123',  
            'password':'456'
        }
    }
    length = 0;
    es = models.Article.objects.all()
    for e in es:
        length = length +1
    article = models.Article.objects.get(pk=random.randint(1,length))
    data1 = {
        'info' : {
            'username':article.title,
            'password':article.content
        }
    }
    return HttpResponse(json.dumps(data1),content_type="application/json")
def seatJson(request):
    seatNum = request.GET['seatNo']
    seat = models.Seat.objects.get(seatNo=seatNum)
    data = {
                'seatNo':seat.seatNo,
	        'st':seat.st,
                'userId':seat.userId
    	   }
    return HttpResponse(json.dumps(data),content_type="application/json")
def getArticle(request):
    a = request.GET['a']
    article = models.Article.objects.get(pk=a)
    return render(request, 'home.html', {'article': article})
def ajax(request):
    a = request.GET['a']
    return render(request, 'ajax.html', {'a': a})
def add2(request, a, b):
    c = int(a) + int(b)
    return HttpResponse(str(c))
def home(request):
    TutorialList = ["HTML", "CSS", "jQuery", "Python", "Django"]
    info_dict = {'site': u'自强学堂', 'content': u'各种IT技术教程'}
    List = map(str, range(100))
    article = models.Article.objects.get(pk=1) 
    return render(request, 'home.html', {'article': article})
def index(request):
    if request.method == 'POST':# 当提交表单时
     
        form = AddForm(request.POST) # form 包含提交的数据
         
        if form.is_valid():# 如果提交的数据合法
            a = form.cleaned_data['a']
            b = form.cleaned_data['b']
            return HttpResponse(str(int(a) + int(b)))
     
    else:# 当正常访问时
        form = AddForm()
        from_email = settings.DEFAULT_FROM_EMAIL
        message1 = ('Subject here', 'Here is the message', from_email, ['854126242@qq.com'])
        message2 = ('Another Subject', 'Here is another message', from_email, ['854126242@qq.com'])
        send_mass_mail((message1, message2), fail_silently=False)
    return render(request, 'index.html', {'form': form})
def seatChoose(request):
    seatNo = request.GET['seatNo']
    st = request.GET['st']
    seatChoose = models.Seat.objects.get(seatNo=seatNo)
    seatChoose.st = st
    seatChoose.save()
    return HttpResponse("Choose Successfully!")
def seatChooseWithID(request):
    seatNo = request.GET['seatNo']
    st = request.GET['st']
    ID = request.GET['userId']
    seatChoose = models.Seat.objects.get(seatNo=seatNo)
    seatChoose.st = st
    seatChoose.userId = ID
    seatChoose.save()
    return HttpResponse("Choose With ID Successfully!")
def seat(request):
    seat_1_1 = models.Seat.objects.get(seatNo='1_1')
    seat_1_2 = models.Seat.objects.get(seatNo='1_2')
    seat_1_3 = models.Seat.objects.get(seatNo='1_3')
    seat_1_4 = models.Seat.objects.get(seatNo='1_4')
    seat_1_5 = models.Seat.objects.get(seatNo='1_5')
    seat_1_6 = models.Seat.objects.get(seatNo='1_6')
    seat_1_7 = models.Seat.objects.get(seatNo='1_7')
    seat_1_8 = models.Seat.objects.get(seatNo='1_8')
    seat_1_9 = models.Seat.objects.get(seatNo='1_9')
    seat_1_10 = models.Seat.objects.get(seatNo='1_10')
    seat_1_11 = models.Seat.objects.get(seatNo='1_11')
    seat_1_16 = models.Seat.objects.get(seatNo='1_16')
    seat_1_17 = models.Seat.objects.get(seatNo='1_17')
    seat_1_18 = models.Seat.objects.get(seatNo='1_18')
    seat_1_19 = models.Seat.objects.get(seatNo='1_19')
    seat_1_20 = models.Seat.objects.get(seatNo='1_20')
    seat_1_21 = models.Seat.objects.get(seatNo='1_21')
    seat_1_22 = models.Seat.objects.get(seatNo='1_22')
    seat_1_23 = models.Seat.objects.get(seatNo='1_23')
    seat_1_24 = models.Seat.objects.get(seatNo='1_24')
    seat_1_25 = models.Seat.objects.get(seatNo='1_25')
    seat_2_1 = models.Seat.objects.get(seatNo='2_1')
    seat_2_2 = models.Seat.objects.get(seatNo='2_2')
    seat_2_3 = models.Seat.objects.get(seatNo='2_3')
    seat_2_4 = models.Seat.objects.get(seatNo='2_4')
    seat_2_5 = models.Seat.objects.get(seatNo='2_5')
    seat_2_6 = models.Seat.objects.get(seatNo='2_6')
    seat_2_7 = models.Seat.objects.get(seatNo='2_7')
    seat_2_8 = models.Seat.objects.get(seatNo='2_8')
    seat_2_9 = models.Seat.objects.get(seatNo='2_9')
    seat_2_10 = models.Seat.objects.get(seatNo='2_10')
    seat_2_11 = models.Seat.objects.get(seatNo='2_11')
    seat_2_16 = models.Seat.objects.get(seatNo='2_16')
    seat_2_17 = models.Seat.objects.get(seatNo='2_17')
    seat_2_18 = models.Seat.objects.get(seatNo='2_18')
    seat_2_19 = models.Seat.objects.get(seatNo='2_19')
    seat_2_20 = models.Seat.objects.get(seatNo='2_20')
    seat_2_21 = models.Seat.objects.get(seatNo='2_21')
    seat_2_22 = models.Seat.objects.get(seatNo='2_22')
    seat_2_23 = models.Seat.objects.get(seatNo='2_23')
    seat_2_24 = models.Seat.objects.get(seatNo='2_24')
    seat_2_25 = models.Seat.objects.get(seatNo='2_25')
    seat_4_1 = models.Seat.objects.get(seatNo='4_1')
    seat_4_2 = models.Seat.objects.get(seatNo='4_2')
    seat_4_3 = models.Seat.objects.get(seatNo='4_3')
    seat_4_4 = models.Seat.objects.get(seatNo='4_4')
    seat_4_5 = models.Seat.objects.get(seatNo='4_5')
    seat_4_6 = models.Seat.objects.get(seatNo='4_6')
    seat_4_7 = models.Seat.objects.get(seatNo='4_7')
    seat_4_8 = models.Seat.objects.get(seatNo='4_8')
    seat_4_9 = models.Seat.objects.get(seatNo='4_9')
    seat_4_10 = models.Seat.objects.get(seatNo='4_10')
    seat_4_11 = models.Seat.objects.get(seatNo='4_11')
    seat_4_16 = models.Seat.objects.get(seatNo='4_16')
    seat_4_17 = models.Seat.objects.get(seatNo='4_17')
    seat_4_18 = models.Seat.objects.get(seatNo='4_18')
    seat_4_19 = models.Seat.objects.get(seatNo='4_19')
    seat_4_20 = models.Seat.objects.get(seatNo='4_20')
    seat_4_21 = models.Seat.objects.get(seatNo='4_21')
    seat_4_22 = models.Seat.objects.get(seatNo='4_22')
    seat_4_23 = models.Seat.objects.get(seatNo='4_23')
    seat_4_24 = models.Seat.objects.get(seatNo='4_24')
    seat_4_25 = models.Seat.objects.get(seatNo='4_25')
    seat_5_1 = models.Seat.objects.get(seatNo='5_1')
    seat_5_2 = models.Seat.objects.get(seatNo='5_2')
    seat_5_3 = models.Seat.objects.get(seatNo='5_3')
    seat_5_4 = models.Seat.objects.get(seatNo='5_4')
    seat_5_5 = models.Seat.objects.get(seatNo='5_5')
    seat_5_6 = models.Seat.objects.get(seatNo='5_6')
    seat_5_7 = models.Seat.objects.get(seatNo='5_7')
    seat_5_8 = models.Seat.objects.get(seatNo='5_8')
    seat_5_9 = models.Seat.objects.get(seatNo='5_9')
    seat_5_10 = models.Seat.objects.get(seatNo='5_10')
    seat_5_11 = models.Seat.objects.get(seatNo='5_11')
    seat_5_16 = models.Seat.objects.get(seatNo='5_16')
    seat_5_17 = models.Seat.objects.get(seatNo='5_17')
    seat_5_18 = models.Seat.objects.get(seatNo='5_18')
    seat_5_19 = models.Seat.objects.get(seatNo='5_19')
    seat_5_20 = models.Seat.objects.get(seatNo='5_20')
    seat_5_21 = models.Seat.objects.get(seatNo='5_21')
    seat_5_22 = models.Seat.objects.get(seatNo='5_22')
    seat_5_23 = models.Seat.objects.get(seatNo='5_23')
    seat_5_24 = models.Seat.objects.get(seatNo='5_24')
    seat_5_25 = models.Seat.objects.get(seatNo='5_25')
    seat_7_1 = models.Seat.objects.get(seatNo='7_1')
    seat_7_2 = models.Seat.objects.get(seatNo='7_2')
    seat_7_3 = models.Seat.objects.get(seatNo='7_3')
    seat_7_4 = models.Seat.objects.get(seatNo='7_4')
    seat_7_5 = models.Seat.objects.get(seatNo='7_5')
    seat_7_6 = models.Seat.objects.get(seatNo='7_6')
    seat_7_7 = models.Seat.objects.get(seatNo='7_7')
    seat_7_8 = models.Seat.objects.get(seatNo='7_8')
    seat_7_9 = models.Seat.objects.get(seatNo='7_9')
    seat_7_10 = models.Seat.objects.get(seatNo='7_10')
    seat_7_11 = models.Seat.objects.get(seatNo='7_11')
    seat_7_16 = models.Seat.objects.get(seatNo='7_16')
    seat_7_17 = models.Seat.objects.get(seatNo='7_17')
    seat_7_18 = models.Seat.objects.get(seatNo='7_18')
    seat_7_19 = models.Seat.objects.get(seatNo='7_19')
    seat_7_20 = models.Seat.objects.get(seatNo='7_20')
    seat_7_21 = models.Seat.objects.get(seatNo='7_21')
    seat_7_22 = models.Seat.objects.get(seatNo='7_22')
    seat_7_23 = models.Seat.objects.get(seatNo='7_23')
    seat_7_24 = models.Seat.objects.get(seatNo='7_24')
    seat_7_25 = models.Seat.objects.get(seatNo='7_25')
    seat_8_1 = models.Seat.objects.get(seatNo='8_1')
    seat_8_2 = models.Seat.objects.get(seatNo='8_2')
    seat_8_3 = models.Seat.objects.get(seatNo='8_3')
    seat_8_4 = models.Seat.objects.get(seatNo='8_4')
    seat_8_5 = models.Seat.objects.get(seatNo='8_5')
    seat_8_6 = models.Seat.objects.get(seatNo='8_6')
    seat_8_7 = models.Seat.objects.get(seatNo='8_7')
    seat_8_8 = models.Seat.objects.get(seatNo='8_8')
    seat_8_9 = models.Seat.objects.get(seatNo='8_9')
    seat_8_10 = models.Seat.objects.get(seatNo='8_10')
    seat_8_11 = models.Seat.objects.get(seatNo='8_11')
    seat_8_16 = models.Seat.objects.get(seatNo='8_16')
    seat_8_17 = models.Seat.objects.get(seatNo='8_17')
    seat_8_18 = models.Seat.objects.get(seatNo='8_18')
    seat_8_19 = models.Seat.objects.get(seatNo='8_19')
    seat_8_20 = models.Seat.objects.get(seatNo='8_20')
    seat_8_21 = models.Seat.objects.get(seatNo='8_21')
    seat_8_22 = models.Seat.objects.get(seatNo='8_22')
    seat_8_23 = models.Seat.objects.get(seatNo='8_23')
    seat_8_24 = models.Seat.objects.get(seatNo='8_24')
    seat_8_25 = models.Seat.objects.get(seatNo='8_25')
    seat_10_1 = models.Seat.objects.get(seatNo='10_1')
    seat_10_2 = models.Seat.objects.get(seatNo='10_2')
    seat_10_3 = models.Seat.objects.get(seatNo='10_3')
    seat_10_4 = models.Seat.objects.get(seatNo='10_4')
    seat_10_5 = models.Seat.objects.get(seatNo='10_5')
    seat_10_6 = models.Seat.objects.get(seatNo='10_6')
    seat_10_7 = models.Seat.objects.get(seatNo='10_7')
    seat_10_8 = models.Seat.objects.get(seatNo='10_8')
    seat_10_9 = models.Seat.objects.get(seatNo='10_9')
    seat_10_10 = models.Seat.objects.get(seatNo='10_10')
    seat_10_11 = models.Seat.objects.get(seatNo='10_11')
    seat_10_16 = models.Seat.objects.get(seatNo='10_16')
    seat_10_17 = models.Seat.objects.get(seatNo='10_17')
    seat_10_18 = models.Seat.objects.get(seatNo='10_18')
    seat_10_19 = models.Seat.objects.get(seatNo='10_19')
    seat_10_20 = models.Seat.objects.get(seatNo='10_20')
    seat_10_21 = models.Seat.objects.get(seatNo='10_21')
    seat_10_22 = models.Seat.objects.get(seatNo='10_22')
    seat_10_23 = models.Seat.objects.get(seatNo='10_23')
    seat_10_24 = models.Seat.objects.get(seatNo='10_24')
    seat_10_25 = models.Seat.objects.get(seatNo='10_25')
    seat_11_1 = models.Seat.objects.get(seatNo='11_1')
    seat_11_2 = models.Seat.objects.get(seatNo='11_2')
    seat_11_3 = models.Seat.objects.get(seatNo='11_3')
    seat_11_4 = models.Seat.objects.get(seatNo='11_4')
    seat_11_5 = models.Seat.objects.get(seatNo='11_5')
    seat_11_6 = models.Seat.objects.get(seatNo='11_6')
    seat_11_7 = models.Seat.objects.get(seatNo='11_7')
    seat_11_8 = models.Seat.objects.get(seatNo='11_8')
    seat_11_9 = models.Seat.objects.get(seatNo='11_9')
    seat_11_10 = models.Seat.objects.get(seatNo='11_10')
    seat_11_11 = models.Seat.objects.get(seatNo='11_11')
    seat_11_16 = models.Seat.objects.get(seatNo='11_16')
    seat_11_17 = models.Seat.objects.get(seatNo='11_17')
    seat_11_18 = models.Seat.objects.get(seatNo='11_18')
    seat_11_19 = models.Seat.objects.get(seatNo='11_19')
    seat_11_20 = models.Seat.objects.get(seatNo='11_20')
    seat_11_21 = models.Seat.objects.get(seatNo='11_21')
    seat_11_22 = models.Seat.objects.get(seatNo='11_22')
    seat_11_23 = models.Seat.objects.get(seatNo='11_23')
    seat_11_24 = models.Seat.objects.get(seatNo='11_24')
    seat_11_25 = models.Seat.objects.get(seatNo='11_25')
    return render(request,'seat.plist',locals())

