from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('',views.home, name="home"),
    path('signup',views.signup,name="signup"),
    path('signin',views.signin,name="signin"),
    path('signout',views.signout,name="signout"),
    path('previous',views.previous,name="previous"),
    path('watch_video',views.camera,name="watch_video"),
    path('video',views.video,name="video"),
    path('upload',views.upload,name="upload"),
    path('stat',views.stat,name="stat"),
    
    path('video_list',views.video_list,name="video_list"),
    path('videos/<str:pk>/delete/', views.VideoDeleteView.as_view(), name='delete_video'),
    
    path('process_frames/', views.process_frames, name='process_frames'),
    path('get_video_sources/',views.get_video_sources, name='get_video_sources'),
    
]
