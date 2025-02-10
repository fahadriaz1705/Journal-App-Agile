from django.contrib import admin
from .models import JournalEntry
from .models import Tag
from .models import Attachment
from .models import Theme
# Register your models here.

admin.site.register(JournalEntry)
admin.site.register(Tag)
admin.site.register(Attachment)
admin.site.register(Theme)