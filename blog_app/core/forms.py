from django import forms
from .models import User, Category, Post
from django.forms.widgets import FileInput, TextInput, EmailInput, Textarea


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'category', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget = TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter title'
        })
        self.fields['description'].widget = Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter description',
            'rows': 6,
            'style': 'resize: None;'
        })
        self.fields['category'].widget = forms.Select(attrs={
            'class': 'form-control'
        })
        self.fields['image'].widget = FileInput(attrs={
            'class': 'form-control',
        })
        self.fields['category'].choices = [(cat.id, cat) for cat in Category.objects.all()]


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'nickname', 'email', 'profile_photo', 'bio', 'fav_sub']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = TextInput(attrs={
            'class': 'form-control',
        })
        self.fields['nickname'].widget = TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nickname'
        })
        self.fields['email'].widget = EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
        self.fields['profile_photo'].widget = FileInput(attrs={
            'class': 'form-control'
        })
        self.fields['bio'].widget = Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Bio',
            'style': 'resize: None;'
        })
        self.fields['fav_sub'].widget = forms.Select(attrs={
            'class': 'form-control'
        })
        self.fields['fav_sub'].choices = [(cat.id, cat.name) for cat in Category.objects.all()]
