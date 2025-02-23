from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .models import Tag
from .models import JournalEntry

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        userId = request.user.id
        allJournals = JournalEntry.objects.filter(user=userId)
        allTags = Tag.objects.filter(journalentry__user=request.user).distinct()
        params = {'allJournals': allJournals,'allTags': allTags}
        return render(request,'journalApp/index.html',params)
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
        user.save()
        messages.success(request,'Your account has been successfully created')
        return redirect('home')
    else:
        return HttpResponse('Error: 404(Not Found)')
def logOut(request):
    logout(request)
    messages.success(request,'You have successfully logged out')
    return redirect('home')
def newEntry(request):
    allTags = Tag.objects.filter(journalentry__user=request.user).distinct()
    params = {'allTags': allTags}
    return render(request,'journalApp/journalEntry.html',params)
def createEntry(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        existTagId = request.POST.get('existingTag')
        newTagName = request.POST.get('newTag')

        # Decide whether to use existing tag or create a new one
        if newTagName:
            tag, created = Tag.objects.get_or_create(name=newTagName)
        elif existTagId:
            tag = Tag.objects.get(tag_id=existTagId)
        else:
            tag = None
        # Create the journal entry
        JournalEntry.objects.create(user=request.user,title=title,content=content,tag=tag)
        # Redirect
        return redirect('index')
    else:
        messages.error(request,'Sorry we encountered an error try again')
        return redirect('newEntry')

