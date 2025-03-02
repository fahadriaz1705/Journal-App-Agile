from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Tag
from .models import JournalEntry
from .models import Attachment
from django.utils import timezone
from xhtml2pdf import pisa
from io import BytesIO

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        userId = request.user.id
        allJournals = JournalEntry.objects.filter(user=userId)
        latestJournal = JournalEntry.objects.filter(user=request.user).order_by('-created_at').first()
        allTags = Tag.objects.filter(journalentry__user=request.user).distinct()
        today = timezone.now()
        params = {'allJournals': allJournals,'allTags': allTags,'latestJournal': latestJournal,'today':today}
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

        # Check for existing user/ email
        if User.objects.filter(username=userName).exists():
            messages.error(request, 'This username already exists. Please try a different one.')
            return redirect('register')

        if User.objects.filter(email=userEmail).exists():
            messages.error(request, 'This email already exists. Please try a different one.')
            return redirect('register')

        # Some basic checks:
        if len(userName) > 10:
            messages.error(request, 'Username must be less than 10 characters.')
            return redirect('register')

        if not userName.isalnum():
            messages.error(request, 'Username should only contain alphanumeric characters.')
            return redirect('register')

        if pass1 != pass2:
            messages.error(request, 'Both passwords did not match, please try again.')
            return redirect('register')
        try:
            password_validation.validate_password(pass1, user=None)
        except ValidationError as e:
            for error in e:
                messages.error(request, error)
            return redirect('register')

        # If we reach here, the password is valid per Django's validators
        user = User.objects.create_user(username=userName, email=userEmail, password=pass1)
        user.save()
        messages.success(request, 'Your account has been successfully created')
        return redirect('home')

    else:
        return HttpResponse('Error: 404 (Not Found)')
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
def changePass(request):
    if not request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save() 
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profSetting')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'journalApp/change_password.html', {'form': form})
@login_required
def delData(request):
    if request.method == 'POST':
        JournalEntry.objects.filter(user=request.user).delete()
        Tag.objects.filter(user=request.user).delete()
        messages.success(request, "All your journal data has been deleted.")
        return redirect('profSetting')
    else:
        messages.error(request, "Invalid request.")
        return redirect('profSetting')
@login_required
def delAccount(request):
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('home')
    else:
        messages.error(request, "Invalid request type.")
        return redirect('profSetting')