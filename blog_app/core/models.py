from django.db import models
from django.contrib.auth.models import User, AbstractUser

'''
User model:
    new ideas:
        followers(?)(need to make a new diagram for this.. and look up for m2m diagrams and how they work.),
'''

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

class User(AbstractUser):
    nickname = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, max_length=254)
    profile_photo = models.ImageField(null=True, blank=True, default="default.png")
    bio = models.TextField(max_length=500, null=True, blank=True)
    fav_sub = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    REQUIRED_FIELDS = []

class Post(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=1000)
    image = models.ImageField(blank= True, null=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, db_constraint=False)
    
    created = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return self.title

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[0:50]

