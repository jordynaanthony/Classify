from django.urls import path, include 
from django.contrib import admin

from . import views
app_name = 'classify'
urlpatterns = [
    path('', views.index, name='index'),
    path('map', views.map, name='map'),
    path('user', views.user, name='user'),
    path('user/schedule', views.schedule, name='schedule'),
    path('user/friends', views.friends, name='friends'),
    path('user/friend_search', views.friend_search, name='friend_search'),
    path('send_friend_request/<int:userID>/',views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:requestID>/',views.accept_friend_request, name='accept_friend_request'),
    path('decline_friend_request/<int:requestID>/',views.decline_friend_request, name='decline_friend_request'),
]