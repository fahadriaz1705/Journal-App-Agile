from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('logIn/',views.logIn,name="logIn"),
    path('signUp/',views.signUp,name="signUp"),
    path('logOut/',views.logOut,name="logOut"),
]