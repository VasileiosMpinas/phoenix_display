from django import forms
from .models import Video

class VideoForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('Άνδρας', 'Άνδρας'),
        ('Γυναίκα', 'Γυναίκα'),
    ]
    gender_tag = forms.ChoiceField(label="Ετικέτα φύλου", choices=GENDER_CHOICES, required=True)
    title = forms.CharField(label="Τίτλος", max_length=10, required=True)
    
    class Meta:
        model = Video
        fields = ['title', 'gender_tag', 'video_file']
        labels = {
            'video_file': 'Αρχείο βίντεο',
        }