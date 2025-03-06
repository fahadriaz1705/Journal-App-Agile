
from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=1)

    def __str__(self):
        return self.name

class JournalEntry(models.Model):
    entry_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class Attachment(models.Model):
    attachment_id = models.AutoField(primary_key=True)
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='attachments')
    image = models.ImageField(upload_to='journal_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.journal_entry.title}"

class Theme(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='theme')
    primary_color = models.CharField(max_length=7, default="#383940")  
    secondary_color = models.CharField(max_length=7, default="#43545b")  
    tertiary_color = models.CharField(max_length=7, default="#7b96a2")  
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Theme for {self.user.username}"