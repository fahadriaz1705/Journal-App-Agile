from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
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
from .models import Theme
from django.utils import timezone
from xhtml2pdf import pisa
from io import BytesIO
import requests

# Create your views here.
def index(request):
    # check if the user is authenticated
    if request.user.is_authenticated:
        # get the currently logged-in user's id
        userId = request.user.id
        # retrieve all journal entries belonging to the user, ordered from newest to oldest
        allJournals = JournalEntry.objects.filter(user=userId).order_by('-created_at')
        # get the latest journal entry for the user
        latestJournal = JournalEntry.objects.filter(user=request.user).order_by('-created_at').first()
        # retrieve all unique tags associated with the user's journal entries
        allTags = Tag.objects.filter(journalentry__user=request.user).distinct()
        # get the current date and time
        today = timezone.now()
        # store all retrieved data in a dictionary to pass it to the template
        params = {'allJournals': allJournals, 'allTags': allTags, 'latestJournal': latestJournal, 'today': today}
        # render the index page with the retrieved data
        return render(request, 'journalApp/index.html', params)

def logIn(request):
    # check if the request method is post (user submitted the login form)
    if request.method == 'POST':
        # retrieve the username and password from the form data
        userName = request.POST.get('username')
        pass1 = request.POST.get('password')
        # authenticate the user based on the provided credentials
        user = authenticate(username=userName, password=pass1)
        # if authentication is successful, log the user in
        if user is not None:
            login(request, user)
            # display a success message to the user
            messages.success(request, 'you have been successfully logged in')
            # redirect the user to the index page (dashboard)
            return redirect('index')
        else:
            # if authentication fails, display an error message
            messages.error(request, 'sorry, you entered wrong credentials, please try again')
            # redirect the user back to the home page
            return redirect('home')

def signUp(request):
    # check if the request method is post (user submitted the signup form)
    if request.method == 'POST':
        # retrieve username, email, and passwords from the form data
        userName = request.POST.get('usernameSu')
        userEmail = request.POST.get('emailSu')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        # check if the username is already taken
        if User.objects.filter(username=userName).exists():
            messages.error(request, 'this username already exists. please try a different one.')
            return redirect('register')

        # check if the email is already used by another user
        if User.objects.filter(email=userEmail).exists():
            messages.error(request, 'this email already exists. please try a different one.')
            return redirect('register')

        # ensure the username is not longer than 10 characters
        if len(userName) > 10:
            messages.error(request, 'username must be less than 10 characters.')
            return redirect('register')

        # ensure the username contains only letters and numbers
        if not userName.isalnum():
            messages.error(request, 'username should only contain alphanumeric characters.')
            return redirect('register')

        # check if both entered passwords match
        if pass1 != pass2:
            messages.error(request, 'both passwords did not match, please try again.')
            return redirect('register')

        # validate the password using django's built-in password validation
        try:
            password_validation.validate_password(pass1, user=None)
        except ValidationError as e:
            # if the password fails validation, display the validation errors
            for error in e:
                messages.error(request, error)
            return redirect('register')

        # create a new user account with the provided details
        user = User.objects.create_user(username=userName, email=userEmail, password=pass1)
        # save the user to the database
        user.save()
        # display a success message
        messages.success(request, 'your account has been successfully created')
        # redirect the user to the home page
        return redirect('home')

    else:
        # return a 404 error if the page is accessed without a post request
        return HttpResponse('error: 404 (not found)')

def logOut(request):
    # log out the current user
    logout(request)
    # display a success message confirming logout
    messages.success(request, 'you have successfully logged out')
    # redirect the user back to the home page
    return redirect('home')

def newEntry(request):
    # retrieve all tags created by the logged-in user
    allTags = Tag.objects.filter(user=request.user)
    # store the retrieved tags in a dictionary to pass it to the template
    params = {'allTags': allTags}
    # render the new journal entry page with the list of tags
    return render(request, 'journalApp/journalEntry.html', params)
def createEntry(request):
    # check if the request method is post (user submitted the create journal form)
    if request.method == 'POST':

        # retrieve the title and content from the form data
        title = request.POST.get('title')
        content = request.POST.get('content')  

        # check if the user is selecting an existing tag or creating a new one
        existTagId = request.POST.get('existingTag')
        newTagName = request.POST.get('newTag')

        # if the user provided a new tag name, create or retrieve it from the database
        if newTagName:
            tag, created = Tag.objects.get_or_create(name=newTagName, user=request.user)
        # if the user selected an existing tag, retrieve it from the database
        elif existTagId:
            tag = Tag.objects.get(tag_id=existTagId)
        # if no tag was provided, set tag as none
        else:
            tag = None

        # create a new journal entry with the provided details and link it to the user
        newEnt = JournalEntry.objects.create(
            user=request.user,
            title=title,
            content=content,
            tag=tag
        )

        # check if the user uploaded an attachment
        if 'attachment' in request.FILES:
            imgFile = request.FILES['attachment']
            # create an attachment object and link it to the journal entry
            Attachment.objects.create(
                journal_entry=newEnt,
                image=imgFile
            )

        # display a success message
        messages.success(request, "journal entry created successfully!")
        # redirect the user to the dashboard (index page)
        return redirect('index')
    else:
        # if the request is not post, display an error message and redirect to the journal entry creation page
        messages.error(request, 'sorry, we encountered an error. try again.')
        return redirect('newEntry')

def profSetting(request):
    # render the profile settings page
    return render(request,'journalApp/settings.html')

def viewEntry(request, entry_id):
    # retrieve the journal entry based on its id
    journal = JournalEntry.objects.get(pk=entry_id)

    # pass the journal entry to the template
    params = {'journal': journal}
    return render(request, 'journalApp/viewJournalEntry.html', params)

def downloadEntry(request, entry_id):
    # retrieve the journal entry using its id
    journal = JournalEntry.objects.get(pk=entry_id)

    # get all attachments linked to this journal entry
    attachments = journal.attachments.all()
    attachmentUrl = [
        request.build_absolute_uri(a.image.url) for a in attachments  # create full url for each attachment
    ]

    # create the context dictionary to pass data to the pdf template
    context = {
        'journal': journal,
        'attachmentUrl': attachmentUrl,
    }

    # render the pdf template with journal data and convert it to an html string
    htmlString = render(request, 'journalApp/pdf_template.html', context).content.decode('utf-8')

    # create a new pdf file in memory
    pdfFile = BytesIO() 
    # use pisa to convert the html string into a pdf file
    pisa_status = pisa.CreatePDF(src=htmlString, dest=pdfFile)

    # if there was an error in pdf generation, return the html content with an error message
    if pisa_status.err:
        return HttpResponse('we had some errors <pre>' + htmlString + '</pre>')
    else:
        # if pdf generation is successful, return the pdf file as a download
        pdfFile.seek(0)  # reset file pointer to start
        response = HttpResponse(pdfFile.read(), content_type='application/pdf')
        filename = f"{journal.title}.pdf"
        content_disposition = f'attachment; filename="{filename}"'
        response['Content-Disposition'] = content_disposition
        return response

def delEntry(request, entry_id):
    # check if the user is authenticated before deleting a journal entry
    if not request.user.is_authenticated:
        return redirect('logIn')

    # retrieve the journal entry based on its id
    journal = JournalEntry.objects.get(pk=entry_id)

    # delete the journal entry from the database
    journal.delete()

    # display a success message
    messages.success(request, "journal entry deleted successfully.")
    # redirect the user back to the dashboard
    return redirect('index')

def changePass(request):
    # check if the user is authenticated before allowing password change
    if not request.user.is_authenticated:
        return redirect('home')

    # check if the request method is post (user submitted the change password form)
    if request.method == 'POST':
        # create a password change form with the user's current data
        form = PasswordChangeForm(user=request.user, data=request.POST)
        # check if the form data is valid
        if form.is_valid():
            # save the new password
            user = form.save() 
            # update the user's session so they remain logged in
            update_session_auth_hash(request, user)
            # display a success message
            messages.success(request, 'your password was successfully updated!')
            # redirect the user to the profile settings page
            return redirect('profSetting')
        else:
            # if the form is not valid, display an error message
            messages.error(request, 'please correct the error below.')
    else:
        # if no post request is received, display the password change form
        form = PasswordChangeForm(user=request.user)

    # render the change password page with the form
    return render(request, 'journalApp/change_password.html', {'form': form})
@login_required
def delData(request):
    # check if the request method is post (ensuring data is not deleted via a get request)
    if request.method == 'POST':
        # delete all journal entries belonging to the logged-in user
        JournalEntry.objects.filter(user=request.user).delete()
        # delete all tags associated with the user's journal entries
        Tag.objects.filter(user=request.user).delete()
        # display a success message
        messages.success(request, "all your journal data has been deleted.")
        # redirect user to the profile settings page
        return redirect('profSetting')
    else:
        # if the request is not post, show an error message and redirect
        messages.error(request, "invalid request.")
        return redirect('profSetting')

@login_required
def delAccount(request):
    # check if the request method is post to prevent accidental account deletion
    if request.method == 'POST':
        # delete the currently logged-in user from the database
        request.user.delete()
        # display a success message
        messages.success(request, "your account has been deleted.")
        # redirect the user to the home page after deletion
        return redirect('home')
    else:
        # if the request is not post, show an error message and redirect
        messages.error(request, "invalid request type.")
        return redirect('profSetting')

@login_required
def updateTheme(request):
    # check if the request method is post (ensuring theme update is not done via a get request)
    if request.method == 'POST':
        # retrieve the colors from the form submission
        primary = request.POST.get('primary_color')
        secondary = request.POST.get('secondary_color')
        tertiary = request.POST.get('tertiary_color')

        # check if the user already has a theme, if not, create one
        theme, created = Theme.objects.get_or_create(user=request.user)
        # update the theme with the new colors
        theme.primary_color = primary
        theme.secondary_color = secondary
        theme.tertiary_color = tertiary
        # save the updated theme
        theme.save()

        # display a success message
        messages.success(request, 'your theme has been updated!')
        # redirect user to the profile settings page
        return redirect('profSetting')
    else:
        # if the request is not post, show an error message and redirect
        messages.error(request, 'invalid request type.')
        return redirect('profSetting')

def editEntry(request, entry_id):
    # retrieve the journal entry based on its id and ensure it belongs to the logged-in user
    journal = JournalEntry.objects.get(pk=entry_id, user=request.user)

    # check if the request method is post (indicating an update)
    if request.method == 'POST':
        # retrieve the updated title and content from the form submission
        title = request.POST.get('title')
        content = request.POST.get('content')
        existing_tag_id = request.POST.get('existingTag')
        new_tag_name = request.POST.get('newTag')

        # update the journal entry's title and content
        journal.title = title
        journal.content = content

        # check if a new tag is provided, create or get it
        if new_tag_name:
            tag, _ = Tag.objects.get_or_create(name=new_tag_name, user=request.user)
            journal.tag = tag
        # check if an existing tag is selected, assign it to the journal
        elif existing_tag_id:
            journal.tag = Tag.objects.get(tag_id=existing_tag_id, user=request.user)
        else:
            # if no tag is provided, set it to none
            journal.tag = None

        # check if the user wants to remove existing attachments
        remove_existing = request.POST.get('remove_attachment')
        if remove_existing == 'on':
            # delete all attachments linked to the journal entry
            journal.attachments.all().delete()

        # check if a new attachment is uploaded
        if 'new_attachment' in request.FILES:
            image_file = request.FILES['new_attachment']
            # create a new attachment linked to the journal entry
            Attachment.objects.create(
                journal_entry=journal,
                image=image_file
            )

        # save the updated journal entry
        journal.save()
        
        # display a success message
        messages.success(request, "entry updated successfully!")
        # redirect user to the view entry page
        return redirect('viewEntry', entry_id=journal.entry_id)
    
    else:
        # retrieve all unique tags created by the user
        all_tags = Tag.objects.filter(user=request.user).distinct()
        # pass journal and tag data to the template
        context = {
            'journal': journal,
            'all_tags': all_tags
        }
        return render(request, 'journalApp/editEntry.html', context)

def zenQuotes(request):
    # try to fetch a random quote from the zenquotes api
    try:
        response = requests.get('https://zenquotes.io/api/random')
        # raise an error if the request fails
        response.raise_for_status()
        # parse the response into json format
        quoteData = response.json()

        # check if the response contains a valid quote
        if isinstance(quoteData, list) and len(quoteData) > 0:
            return JsonResponse(quoteData[0], safe=False)
        else:
            # return an error message if the response format is invalid
            return JsonResponse({'error': 'invalid response format from zenquotes api'}, status=500)

    except requests.RequestException as e:
        # return an error message if there is a request failure
        return JsonResponse({'error': str(e)}, status=500)

def aboutUs(request):
    # render the about us page
    return render(request, 'journalApp/aboutUs.html')