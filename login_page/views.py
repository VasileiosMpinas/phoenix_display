from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .models import Video, FaceData, FaceData2
from .forms import VideoForm
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth.decorators import login_required


import base64
import subprocess
import os
import psutil
import json
import io
from PIL import Image
from datetime import datetime

import cv2
from deepface import DeepFace
import numpy as np
import time
import signal
import sys



# Create your views here.
def home(request):
    return render(request,"login_page/index.html")



@csrf_exempt
def process_frames(request):
    
    #get data from FaceData
    face_data = FaceData.objects.get(user=request.user)

    username = request.user.username
    number_of_faces = face_data.number_of_faces
    number_of_men = face_data.number_of_men
    number_of_women = face_data.number_of_women
    start_time = face_data.start_time
    male_emotions = face_data.male_emotions
    female_emotions = face_data.female_emotions
    
    if request.method == 'POST':
        with transaction.atomic():
            try:
            
                # Use request.body for JSON data
                json_data = json.loads(request.body.decode('utf-8'))
                image_data = json_data.get('image_data', '')

              
                # Check if the data is base64-encoded
                if not image_data.startswith('data:image/jpeg;base64,'):
                    return JsonResponse({'error': 'Invalid image_data format'})

                # Extract the base64-encoded part
                image_data = image_data[len('data:image/jpeg;base64,'):]

                # Decode the base64-encoded image data
                decoded_data = base64.b64decode(image_data)

                # Convert bytes to PIL Image
                image = Image.open(io.BytesIO(decoded_data))

                # Convert PIL Image to NumPy array
                image_array = np.array(image)
            
                # Analyze the frame using DeepFace library
                result = DeepFace.analyze(image_array, actions=['gender', 'emotion'])
            
                ##Gender counters
                manC=0
                womanC=0

                ##Emotion counters

                m_em={'happyC':0,'angryC':0,'disgustC':0,'fearC':0,'sadC':0,'surpriseC':0,'neutralC':0}
                f_em={'happyC':0,'angryC':0,'disgustC':0,'fearC':0,'sadC':0,'surpriseC':0,'neutralC':0}


                for i in range(len(result)):
                            if result[i]['dominant_gender']=='Man':
                                manC+=1
                                if number_of_men<manC:
                                    number_of_men=manC
                                m_em['happyC'],m_em['angryC'],m_em['disgustC'],m_em['fearC'],m_em['sadC'],m_em['surpriseC'],m_em['neutralC']=emotion(result[i]['dominant_emotion'],m_em)

                                male_emotions['happy_people'],male_emotions['angry_people'],male_emotions['disgust_people'],male_emotions['fear_people'],male_emotions['sad_people'],male_emotions['surprise_people'],male_emotions['neutral_people']=global_emotions(m_em,male_emotions)

                            elif  result[i]['dominant_gender']=='Woman':
                                womanC+=1
                                if number_of_women<womanC:
                                    number_of_women=womanC
                                f_em['happyC'],f_em['angryC'],f_em['disgustC'],f_em['fearC'],f_em['sadC'],f_em['surpriseC'],f_em['neutralC']=emotion(result[i]['dominant_emotion'],f_em)

                                female_emotions['happy_people'],female_emotions['angry_people'],female_emotions['disgust_people'],female_emotions['fear_people'],female_emotions['sad_people'],female_emotions['surprise_people'],female_emotions['neutral_people']=global_emotions(f_em,female_emotions)
            

                number_of_faces=number_of_men+number_of_women
                
                
                if(number_of_women>number_of_men):
                        gender_comp = 'Female'
                         
                elif(number_of_women<number_of_men):
                        gender_comp = 'Male'
                        
                else:
                        gender_comp = 'Neutral'
            
                user_instance, created = User.objects.get_or_create(username=username)
                FaceData.objects.update_or_create(user=user_instance, defaults={
                    'number_of_faces':number_of_faces,
                    'number_of_men': number_of_men,
                    'number_of_women': number_of_women,
                    'male_emotions': male_emotions,
                    'female_emotions': female_emotions})
                
                return JsonResponse({
                    'gender_comp': gender_comp
                })
          #      return JsonResponse({'video':video,'gender_comp': gender_comp})
        
            except Exception as e:
             end_time=time.time()
             face_data2 = FaceData2.objects.get(user=request.user)
             number_of_faces2 = face_data2.number_of_faces
             number_of_men2 = face_data2.number_of_men
             number_of_women2 = face_data2.number_of_women
             total_time2=face_data2.total_time
             male_emotions2 = face_data2.male_emotions
             female_emotions2 = face_data2.female_emotions

                

#                try:
 #                   video = Video.objects.get(id=video_id)
  #                  video.number_of_men += number_of_men
   #                 video.number_of_women += number_of_women
                    
    #                if(video.number_of_women>video.number_of_men):
     #                    video.gender_tag = 'Female'
                         
      #              elif(video.number_of_women<video.number_of_men):
       #                 video.gender_tag = 'Male'
                        
        #            else:
         #               video.gender_tag = 'Neutral'
                        
          #          video.save()
           #     except Video.DoesNotExist:
            #        return JsonResponse({'error': 'Video not found'})

                # Update the video views based on the number of people detected
                
    
            number_of_faces+=number_of_faces2
            number_of_men+=number_of_men2
            number_of_women+=number_of_women2
            for i in male_emotions:
                    male_emotions[i]+=male_emotions2[i]
                    female_emotions[i]+=female_emotions2[i]
                
               
            total_time=end_time-start_time
            if (face_data2.total_time<=total_time):
                 face_data2.total_time=total_time
            
            user_instance, created = User.objects.get_or_create(username=username)
            FaceData2.objects.update_or_create(user=user_instance, defaults={
                        'number_of_faces':number_of_faces,
                        'number_of_men': number_of_men,
                        'number_of_women': number_of_women,
                        'total_time' : total_time,
                        'male_emotions': male_emotions,
                        'female_emotions': female_emotions})
                
               
            start_time=time.time()
            number_of_faces=0
            number_of_men=0
            number_of_women=0
            male_emotions={'happy_people':0,'angry_people':0,'disgust_people':0,'fear_people':0,'sad_people':0,'surprise_people':0,'neutral_people':0}
            female_emotions={'happy_people':0,'angry_people':0,'disgust_people':0,'fear_people':0,'sad_people':0,'surprise_people':0,'neutral_people':0}  
                
            FaceData.objects.update_or_create(user=user_instance, defaults={
                        'number_of_faces':number_of_faces,
                        'number_of_men': number_of_men,
                        'number_of_women': number_of_women,
                        'start_time' : end_time,
                        'male_emotions': male_emotions,
                        'female_emotions': female_emotions})


            return JsonResponse({'error': 'Internal Server Error'})
    else:
        return JsonResponse({'error': 'Invalid request method'})
    

def stat(request):
    # Get the face data for the user
    try:
        
        face_data = FaceData2.objects.get(user=request.user)
    

    # Check if it's the first day of the month
        today = datetime.now().day
        if today == 1 and not face_data.is_reset_this_month:
        # Reset the values of the face_data object
            face_data.number_of_faces = 0
            face_data.number_of_men = 0
            face_data.number_of_women = 0
            face_data.total_time = 0
            face_data.male_emotions = {'happy_people':0,'angry_people':0,'disgust_people':0,'fear_people':0,'sad_people':0,'surprise_people':0,'neutral_people':0}  # Reset the dictionary to empty
            face_data.female_emotions = {'happy_people':0,'angry_people':0,'disgust_people':0,'fear_people':0,'sad_people':0,'surprise_people':0,'neutral_people':0}  # Reset the dictionary to empty
            
            face_data.is_reset_this_month = True
            face_data.save()  # Save the changes
        elif today!=1:
            face_data.is_reset_this_month = False

    # Prepare context for rendering
        context = {
            'number_of_faces': face_data.number_of_faces,
            'number_of_men': face_data.number_of_men,
            'number_of_women': face_data.number_of_women,
            'total_time': face_data.total_time,
            'male_emotions': face_data.male_emotions,
            'female_emotions': face_data.female_emotions,

        }

    except FaceData2.DoesNotExist:
        messages.error(request, "Δεν έχει χρησιμοποιηθεί η κάμερα! Πρασπαθήστε μετά την ενεργοποίηση της")
        return redirect('video')

    return render(request, 'login_page/stat.html', context)


def signup(request):
    if request.method=="POST":
        username = request.POST['username']
        fname= request.POST['fname']
        lname= request.POST['lname']
        email= request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name=fname
        myuser.last_name=lname
        
        myuser.save()

        messages.success(request, "Your Account has been created.")
        return redirect('signin')


    return render(request,"login_page/signup.html")

def signin(request):
    if request.method=='POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(request, username=username, password=pass1)

        if user is not None:
            login(request, user)
            user_meta=user._meta
         #   messages.success(request, "You are logged in.")
            return render(request, "login_page/video.html")
        else:
            messages.error(request, "Λάθος όνομα χρήστη ή κωδικός! Παρακαλώ προσπαθήστε ξανά!")
            user = authenticate(request, username=username, password=pass1)
            print(f"Authenticate Result: {user}")
            return redirect('home')


    return render(request,"login_page/signin.html")



def signout(request):
    logout(request)
 #   messages.success(request, "Logged out succefully!")
    return redirect('home')


def previous(request):
    return redirect('video')


class VideoDeleteView(DeleteView):
    model = Video
    template_name = 'login_page/delete_video.html'
    success_url = reverse_lazy('video')
    
    def get_success_url(self):
        return reverse_lazy('video_list')


def camera(request):
    start_time=time.time()
    username = request.user.username
    number_of_faces=0
    number_of_men=0
    number_of_women=0
    male_emotions={'happy_people':0,'angry_people':0,'disgust_people':0,'fear_people':0,'sad_people':0,'surprise_people':0,'neutral_people':0}
    female_emotions={'happy_people':0,'angry_people':0,'disgust_people':0,'fear_people':0,'sad_people':0,'surprise_people':0,'neutral_people':0}  
    
    total_time=0


    user_instance, created = User.objects.get_or_create(username=username)
    FaceData.objects.update_or_create(user=user_instance, defaults={
                'number_of_faces':number_of_faces,
                'number_of_men': number_of_men,
                'number_of_women': number_of_women,
                'start_time' : start_time,
                'male_emotions': male_emotions,
                'female_emotions': female_emotions,})

    if not FaceData2.objects.filter(user=user_instance).exists():
        is_reset_this_month = False
        FaceData2.objects.update_or_create(user=user_instance, defaults={
                'number_of_faces':number_of_faces,
                'number_of_men': number_of_men,
                'number_of_women': number_of_women,
                'total_time' : total_time,
                'male_emotions': male_emotions,
                'female_emotions': female_emotions,
                'is_reset_this_month': is_reset_this_month})
         

    
   # videos = Video.objects.annotate(num_views=Count('facedetection')).order_by('-num_views')
    user = request.user
    
    # Filter videos based on the current user
    videos = Video.objects.filter(user=user)
    
  #  messages.success(request, "Logged in succefully!")
   # video_id_list = [int(video_id) for video_id in video_ids.split(',')]
    
    #videos = Video.objects.filter(pk__in=video_id_list)
    return render(request, 'login_page/watch_video.html', {'videos': videos})






def get_video_sources(request):
    
    user = request.user
    # Filter videos based on the current user
    videos = Video.objects.filter(user=user)
    
    
    # Query all videos and get their sources
    video_data = [{'source': video.video_file.url, 'gender_tag': video.gender_tag} for video in videos]

    return JsonResponse({'video_data': video_data})

def video(request):

    videos = Video.objects.all()
    return render(request, 'login_page/video.html')



@login_required
def upload(request):
    if request.method == 'POST':
        # Create a new VideoForm instance with the POST data and files
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the current user and set it as the user field of the Video instance
            form.instance.user = request.user
            # Save the form to create a new Video object associated with the current user
            form.save()
            return redirect('video')
    else:
        # Render the upload form for GET requests
        form = VideoForm()
    return render(request, 'login_page/upload.html', {'form': form})




def emotion(dom_emotion,em):

        if dom_emotion=='happy':
            em['happyC']+=1
        
        elif dom_emotion=='angry':
            em['angryC']+=1

        elif dom_emotion=='disgust':
            em['disgustC']+=1
    
        elif dom_emotion=='fear':
            em['fearC']+=1

        elif dom_emotion=='sad':
            em['sadC']+=1

        elif dom_emotion=='surprise':
            em['surpriseC']+=1
    
        elif dom_emotion=='neutral':
            em['neutralC']+=1

        return em['happyC'],em['angryC'],em['disgustC'],em['fearC'],em['sadC'],em['surpriseC'],em['neutralC']


def global_emotions(em,emotions):

        if emotions['happy_people']<em['happyC']:
            emotions['happy_people']=em['happyC']

        elif emotions['angry_people']<em['angryC']:
            emotions['angry_people']=em['angryC']

        elif emotions['disgust_people']<em['disgustC']:
            emotions['disgust_people']=em['disgustC']

        elif emotions['fear_people']<em['fearC']:
             emotions['fear_people']=em['fearC']
    
        elif emotions['sad_people']<em['sadC']:
            emotions['sad_people']=em['sadC']

        elif emotions['surprise_people']<em['surpriseC']:
            emotions['surprise_people']=em['surpriseC']
    
        elif emotions['neutral_people']<em['neutralC']:
            emotions['neutral_people']=em['neutralC']

        return emotions['happy_people'], emotions['angry_people'],emotions['disgust_people'],emotions['fear_people'],emotions['sad_people'],emotions['surprise_people'],emotions['neutral_people']


@login_required
def video_list(request):
    user = request.user
    # Filter videos based on the current user
    videos = Video.objects.filter(user=user)
    return render(request, 'login_page/video_list.html', {'videos': videos})