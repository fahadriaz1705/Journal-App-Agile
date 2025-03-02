from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .models import Tag
from .models import JournalEntry
from .models import Attachment
from xhtml2pdf import pisa
from io import BytesIO

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        userId = request.user.id
        allJournals = JournalEntry.objects.filter(user=userId)
        latestJournal = JournalEntry.objects.filter(user=request.user).order_by('-created_at').first()
        allTags = Tag.objects.filter(journalentry__user=request.user).distinct()
        params = {'allJournals': allJournals,'allTags': allTags,'latestJournal': latestJournal}
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
    allTags = Tag.objects.filter(user=request.user)
    params = {'allTags': allTags}
    return render(request,'journalApp/journalEntry.html',params)
def createEntry(request):
    if request.method == 'POST':
        # 1) Grab title and rich-text HTML from the form
        title = request.POST.get('title')
        content = request.POST.get('content')  # This is the raw HTML from the contenteditable div

        # 2) Decide whether to use existing tag or create a new one
        existTagId = request.POST.get('existingTag')
        newTagName = request.POST.get('newTag')
        if newTagName:
            tag, created = Tag.objects.get_or_create(name=newTagName)
        elif existTagId:
            tag = Tag.objects.get(tag_id=existTagId)
        else:
            tag = None

        # 3) Create the journal entry, storing the HTML
        newEnt = JournalEntry.objects.create(
            user=request.user,
            title=title,
            content=content,  # <--- HTML is saved here
            tag=tag
        )

        # 4) Handle file uploads (if any)
        if 'attachment' in request.FILES:
            imgFile = request.FILES['attachment']
            Attachment.objects.create(
                journal_entry=newEnt,
                image=imgFile
            )

        # 5) Redirect or show success message
        messages.success(request, "Journal entry created successfully!")
        return redirect('index')
    else:
        messages.error(request, 'Sorry, we encountered an error. Try again.')
        return redirect('newEntry')
def profSetting(request):
    return render(request,'journalApp/settings.html')
def viewEntry(request, entry_id):
    journal = JournalEntry.objects.get(pk=entry_id)
    # Pass it to the template
    params = {'journal': journal}
    return render(request, 'journalApp/viewJournalEntry.html', params)
def downloadEntry(request, entry_id):
    # 1. Get the journal entry or raise 404
    journal = JournalEntry.objects.get(pk=entry_id)

    # 2. Render HTML template for PDF content
    # We'll pass 'journal' as context
    attachments = journal.attachments.all()
    attachmentUrl = [
        request.build_absolute_uri(a.image.url) for a in attachments
    ]

    context = {
        'journal': journal,
        'attachmentUrl': attachmentUrl,
    }

    htmlString = render(request, 'journalApp/pdf_template.html', context).content.decode('utf-8')

    # 3. Create a PDF using xhtml2pdf
    pdfFile = BytesIO()  # We'll write the PDF data into this file-like buffer
    pisa_status = pisa.CreatePDF(src=htmlString, dest=pdfFile)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + htmlString + '</pre>')
    else:
        # 4. Return the PDF as a download
        pdfFile.seek(0)  # Reset file pointer to start
        response = HttpResponse(pdfFile.read(), content_type='application/pdf')
        filename = f"{journal.title}.pdf"
        content_disposition = f'attachment; filename="{filename}"'
        response['Content-Disposition'] = content_disposition
        return response
