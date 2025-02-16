from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages


# Create your views here.
def index(request):
    return render(request,'journalApp/index.html')
def logIn(request):
    if request.method == 'POST':
        userName = request.POST.get('username')
        pass1 = request.POST.get('password')
        user = authenticate(username = userName,password = pass1)
        if user is not None:
            login(request,user)
            messages.success(request,'You have been successfully logged in')
            return redirect('index')
        else:
            messages.error(request,'Sorry you entered wrong credentials please try again')
            return redirect('home')
def signUp(request):
    if request.method == 'POST':
        userName = request.POST.get('usernameSu')
        userEmail = request.POST.get('emailSu')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        existUser = User.objects.filter(username = userName)
        existEmail = User.objects.filter(email=userEmail)

        if len(userName) > 10:
            messages.error(request,'Username must be less than 10 characters')
            return redirect('home')
        if not pass1 == pass2:
            messages.error(request,'Both passwords didnt match, please try again')
            return redirect('home')
        if not userName.isalnum():
            messages.error(request,'Username should only contain alpha numeric characters')
            return redirect('home')
        if existUser:
            messages.error(request,'This username already exists please try a different one')
            return redirect('home')
        if existEmail:
            messages.error(request,'This email already exists please try a different one')
            return redirect('home')
            
        user = User.objects.create_user(username=userName,email=userEmail,password=pass1)
        # user.first_name = Fname
        # user.last_name = Lname
        user.save()
        messages.success(request,'Your account has been successfully created')
        return redirect('home')
    else:
        return HttpResponse('Error: 404(Not Found)')
def logOut(request):
    logout(request)
    messages.success(request,'You have successfully logged out')
    return redirect('home')
