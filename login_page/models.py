from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin, User
from django.db.models import Count

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


    
class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, primary_key=True)
    gender_tag = models.CharField(max_length=10)
    video_file = models.FileField(upload_to='videos/')
    upload_date = models.DateTimeField(auto_now_add=True)
     #   gender_comp = models.CharField(max_length=10, default='Unknown')
  #  number_of_men = models.IntegerField(default=0)
   # number_of_women = models.IntegerField(default=0)

    def __str__(self):
        return f"Video '{self.title}' uploaded by {self.user.username}"
    
    


class YourModel(models.Model):
    field1 = models.CharField(max_length=255)
    field2 = models.IntegerField()



class FaceData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    number_of_faces = models.IntegerField(default=0)
    number_of_men = models.IntegerField(default=0)
    number_of_women = models.IntegerField(default=0)
    start_time = models.IntegerField(default=0)
    male_emotions = models.JSONField(default=dict)
    female_emotions = models.JSONField(default=dict)

    def __str__(self):
        return f"FaceData for {self.user.username}"
    

class FaceData2(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    number_of_faces = models.IntegerField(default=0)
    number_of_men = models.IntegerField(default=0)
    number_of_women = models.IntegerField(default=0)
    total_time = models.IntegerField(default=0)
    male_emotions = models.JSONField(default=dict)
    female_emotions = models.JSONField(default=dict)
    is_reset_this_month = models.BooleanField(default=False)

    def __str__(self):
        return f"FaceData2 for {self.user.username}"




