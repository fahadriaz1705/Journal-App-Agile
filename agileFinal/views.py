from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return render(request,'agileFinal/login.html')

def register(request):
    return render(request,'agileFinal/signup.html')