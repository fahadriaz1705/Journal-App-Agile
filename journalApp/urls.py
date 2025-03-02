from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('logIn/',views.logIn,name="logIn"),
    path('signUp/',views.signUp,name="signUp"),
    path('logOut/',views.logOut,name="logOut"),
    path('newEntry/',views.newEntry,name="newEntry"),
    path('createEntry/',views.createEntry,name="createEntry"),
    path('profSetting/',views.profSetting,name="profSetting"),
    path('viewEntry/<int:entry_id>/', views.viewEntry, name='viewEntry'),
]