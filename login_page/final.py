import cv2
import imghdr
import sys
#sys.path.append( 'C:\\Users\\Administrator\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages')


from  deepface import DeepFace
import numpy as np
import time
import sys
project_path = 'C:\\Users\\Administrator\\Desktop\\project_visual\\project_visual'  
sys.path.append(project_path)
#sys.path.append('C:\\Users\\kicki\\OneDrive\\Υπολογιστής\\project_visual\\project_visual\\login_page\\')

import django
django.setup()

from django.contrib.auth.models import User
from login_page.models import FaceData

def camera(username,id):
    face_cascade=cv2.CascadeClassifier("C:\\Users\\Administrator\\Desktop\\project_visual\\project_visual\\login_page\\haarcascade_frontalface_default.xml")


    number_of_men=0
    number_of_women=0
    male_emotions={'happy_people':0,'angry_people':0,'disgust_people':0,'fear_people':0,'sad_people':0,'surprise_people':0,'neutral_people':0}
    female_emotions={'happy_people':0,'angry_people':0,'disgust_people':0,'fear_people':0,'sad_people':0,'surprise_people':0,'neutral_people':0}


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


    while True:
        
     #   print(cv2.VideoCaptureInfo())
        video=cv2.VideoCapture(0)
        start_time=time.time()
        
        while video.isOpened():
            _,frame =video.read()
            gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            face=face_cascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5)


            counter=0


            for x,y,w,h in face:
            
                ##Gender counters
                manC=0
                womanC=0

                ##Emotion counters

                m_em={'happyC':0,'angryC':0,'disgustC':0,'fearC':0,'sadC':0,'surpriseC':0,'neutralC':0}
                f_em={'happyC':0,'angryC':0,'disgustC':0,'fearC':0,'sadC':0,'surpriseC':0,'neutralC':0}

 
                img=cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),1)

                try:
                    analyze=DeepFace.analyze(frame,actions=['gender','emotion'])
                    for i in range(len(analyze)):
                        if analyze[i]['dominant_gender']=='Man':
                            manC+=1
                            if number_of_men<manC:
                                number_of_men=manC
                            m_em['happyC'],m_em['angryC'],m_em['disgustC'],m_em['fearC'],m_em['sadC'],m_em['surpriseC'],m_em['neutralC']=emotion(analyze[i]['dominant_emotion'],m_em)

                            male_emotions['happy_people'],male_emotions['angry_people'],male_emotions['disgust_people'],male_emotions['fear_people'],male_emotions['sad_people'],male_emotions['surprise_people'],male_emotions['neutral_people']=global_emotions(m_em,male_emotions)

                        elif  analyze[i]['dominant_gender']=='Woman':
                            womanC+=1
                            if number_of_women<womanC:
                                number_of_women=womanC
                            f_em['happyC'],f_em['angryC'],f_em['disgustC'],f_em['fearC'],f_em['sadC'],f_em['surpriseC'],f_em['neutralC']=emotion(analyze[i]['dominant_emotion'],f_em)

                            female_emotions['happy_people'],female_emotions['angry_people'],female_emotions['disgust_people'],female_emotions['fear_people'],female_emotions['sad_people'],female_emotions['surprise_people'],female_emotions['neutral_people']=global_emotions(f_em,female_emotions)
                
                except:
                    #print("no face")
                    counter+=1
                
                
            cv2.imshow('video',frame)
            key=cv2.waitKey(1)
            
            if counter>=1:
                counter=0
                break

            if key==ord('q'):
                break


        end_time=time.time()
        video.release()
        cv2.destroyAllWindows()

        if key==ord('q'):
            break


#        print("Men :"+str(number_of_men))
 #       print("Women :"+str(number_of_women))
  #      print(end_time-start_time)
   #     print("Male Emotions : [Happy:"+str(male_emotions['happy_people'])+",Angry:"+str(male_emotions['angry_people'])+",Disgust:"+str(male_emotions['disgust_people'])+",Fear:"+str(male_emotions['fear_people'])+",Sad:"+str(male_emotions['sad_people'])+",Surprise:"+str(male_emotions['surprise_people'])+",Neutral:"+str(male_emotions['neutral_people'])+"]")
    #    print("Female Emotions : [Happy:"+str(female_emotions['happy_people'])+",Angry:"+str(female_emotions['angry_people'])+",Disgust:"+str(female_emotions['disgust_people'])+",Fear:"+str(female_emotions['fear_people'])+",Sad:"+str(female_emotions['sad_people'])+",Surprise:"+str(female_emotions['surprise_people'])+",Neutral:"+str(female_emotions['neutral_people'])+"]")
        if (end_time-start_time)>=2:
            number_of_faces=number_of_men+number_of_women

            user_instance, created = User.objects.get_or_create(username=username)
            FaceData.objects.update_or_create(user=user_instance, defaults={
                'number_of_faces':number_of_faces,
                'number_of_men': number_of_men,
                'number_of_women': number_of_women,
                'male_emotions': male_emotions,
                'female_emotions': female_emotions,})            

            file1 = open("MyFile.txt", "a") 

            s=["People:"+str(number_of_faces)+"\n",
            "Men :"+str(number_of_men)+"\n",
            "Women :"+str(number_of_women)+"\n",
            str(end_time-start_time)+"\n",
            "Male Emotions : [Happy:"+str(male_emotions['happy_people'])+",Angry:"+str(male_emotions['angry_people'])+",Disgust:"+str(male_emotions['disgust_people'])+",Fear:"+str(male_emotions['fear_people'])+",Sad:"+str(male_emotions['sad_people'])+",Surprise:"+str(male_emotions['surprise_people'])+",Neutral:"+str(male_emotions['neutral_people'])+"]"+"\n",
            "Female Emotions : [Happy:"+str(female_emotions['happy_people'])+",Angry:"+str(female_emotions['angry_people'])+",Disgust:"+str(female_emotions['disgust_people'])+",Fear:"+str(female_emotions['fear_people'])+",Sad:"+str(female_emotions['sad_people'])+",Surprise:"+str(female_emotions['surprise_people'])+",Neutral:"+str(female_emotions['neutral_people'])+"]"+"\n\n\n"]

            file1.writelines(s)
            file1.close()

    # angry,disgust,fear,happy,sad,surprise,neutral


username = sys.argv[1]
id=sys.argv[2]
camera(username,int(id))