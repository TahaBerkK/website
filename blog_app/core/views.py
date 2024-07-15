from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import UserEditForm, PostForm
from django.views.generic import View, ListView

class IndexView(ListView):
    model = Post
    template_name = "index.html"

    def get(self, request):
        q = request.GET.get('q') if request.GET.get('q') != None else ''

        posts = Post.objects.filter(Q(title__icontains = q)|
                                Q(description__icontains = q)| 
                                Q(category__name__icontains = q)| 
                                Q(host__username__icontains = q)
                                ).order_by('-created')
        paginator = Paginator(posts, 1) #posts get paged by the paginator
        page = request.GET.get('page')
        posts = paginator.get_page(page) #we are getting the page number and sending the values that is on the page we are on
        categories = Category.objects.all()
        
        context ={
            "posts": posts,
            "categories": categories
        }
        return render(request, self.template_name, context)

    def post(self, request):
        pass

class PostCreate(View):
    template_name = "post_creation_edit.html"
    
    @method_decorator(login_required(login_url="user_login"))
    def get(self, request):
        categories = Category.objects.all()
        form = PostForm()
        context = {
            "form": form,
            "categories": categories
            }
        return render(request, self.template_name, context)

    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)
            form.instance.host = request.user
            form.save()
            return redirect("index")
class PostDetails(View):
    model = Post
    template_name = "post_details.html"

    def get(self, request, pk):
        post = Post.objects.get(id=pk)
        comments = Comment.objects.filter(post=post)
        context = {
            "post": post,
            "comments": comments
            }
        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        content = request.POST.get("content") if request.POST.get("content") != '' else None
        if content != None:
            post = Post.objects.get(id=pk)
            user = request.user
            new_comment = Comment.objects.create(user = user, content = content, post = post)
            new_comment.save()
            return redirect("post_details", pk=pk)
        return redirect("post_details", pk=pk)
class PostEdit(View):
    template_name = "post_creation_edit.html"
    @method_decorator(login_required(login_url="user_login"))
    def get(self, request, pk):
        post = Post.objects.get(id=pk)
        categories = Category.objects.all()
        form = PostForm(instance=post)
        context = {
            "form": form,
            "categories": categories,
            "post": post
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        post = Post.objects.get(id=pk)
        if post.image and request.POST.get("profile_photo") != '': 
            post.image.delete()
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("index")
class PostDelete(View):
    template_name = "post_delete.html"

    def get(self, request, pk):
        post = Post.objects.get(id=pk)
        if request.user == post.host:
            post.delete()
        else:
            return HttpResponse("YOU SHOULDNT BE HERE! >:(")

        return redirect("index")

class UserRegister(View):
    template_name = "user_register.html"

    def post(self, request):
        username = request.POST.get("username")
        nickname = request.POST.get("nickname")
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = User.objects.create_user(username=username, password=password, email=email, nickname=nickname)
        user.save()
            
        return redirect("index")
class UserLogin(View):
    template_name = "user_login_register.html"
    
    def get(self, request):
        context={
            "login": True
        }
        return render(request, self.template_name, context)

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        try: 
            user = User.objects.get(username=username)
        except:
            messages.error(request, "Invalid User information")

        user = authenticate(request, username=username, password=password)
        if user == None:
            messages.error(request, "Username or Password is incorrect")
        else:
            login(request, user)
            return redirect("index")
class UserLogout(View):
    
    def get(self, request):
        logout(request)
        return redirect("index")
class UserProfile(View):
    template_name = "user_profile.html"

    def get(self, request, username):
        user = User.objects.get(username = username)
        posts = Post.objects.filter(host = user)

        context = {
            "user": user,
            "posts": posts
        }
        return render(request, "user_profile.html", context)
class UserSettings(View):
    template_name = "user_settings.html"
    
    def get(self, request):
        user = User.objects.get(username = request.user)
        categories = Category.objects.all()
        form = UserEditForm(instance=user)
        context = {
            "form": form,
            "user": user,
            "categories": categories
        }
        return render(request, "user_settings.html", context)
    
    def post(self, request):
        user = User.objects.get(username = request.user)
        if user.profile_photo and request.POST.get("profile_photo") != '':
            user.profile_photo.delete()
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("index")

def index(request):
    
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    posts = Post.objects.filter(Q(title__icontains = q)|
                                Q(description__icontains = q)| 
                                Q(category__name__icontains = q)| 
                                Q(host__username__icontains = q)
                                ).order_by('-created')
    
    categories = Category.objects.all()
    context ={
        "posts": posts,
        "categories": categories
    }
    return render(request, "index.html", context)
@login_required(login_url='user_login')
def post_create(request):
    categories = Category.objects.all()
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=False)
            form.instance.host = request.user
            form.save()
            return redirect("index")
    
    form = PostForm()
    context = {
        "form": form,
        "categories": categories
    }
    return render(request, "post_creation_edit.html", context)
@login_required(login_url='user_login')
def post_edit(request, pk):
    post = Post.objects.get(id=pk)
    categories = Category.objects.all()
    
    if request.method == "POST":
        if post.image:
            post.image.delete()
        form = PostForm(request.POST, request.FILES, instance = post)
        if form.is_valid():
            form.save()
            return redirect("index")

    form = PostForm(instance = post)
    context={
        "form": form,
        "post": post,
        "categories": categories
    }
    return render(request, "post_creation_edit.html", context)
def post_details(request, pk):
    post = Post.objects.get(id = pk)
    comments = Comment.objects.filter(post = pk)
    if request.method == "POST":
        content = request.POST.get("content")
        user = request.user
        new_comment = Comment.objects.create(user = user, content = content, post = post)
        new_comment.save()
        return redirect("post_details", pk=pk)
    
    context = {
        "post": post,
        "comments": comments,
    }
    return render(request, "post_details.html", context)
@login_required(login_url='user_login')
def post_delete(request, pk):
    post = Post.objects.get(id = pk)
    post.delete()
    
    return redirect("index")

def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        nickname = request.POST.get("nickname")
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = User.objects.create_user(username=username, password=password, email=email, nickname=nickname)
        user.save()
        
        return redirect("index")
    
    return render(request, 'user_login_register.html')
def user_login(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try: 
            user = User.objects.get(username=username)
        except:
            messages.error(request, "Invalid User information")

        user = authenticate(request, username=username, password=password)
        if user == None:
            messages.error(request, "Username or Password is incorrect")
        else:
            login(request, user)
            return redirect("index")
    
    context = {
        "login": True
    }
    return render(request, "user_login_register.html", context)
def user_logout(request):
    logout(request)
    return redirect("index")
def user_profile(request, username):
    user = User.objects.get(username = username)
    posts = Post.objects.filter(host = user)

    context = {
        "user": user,
        "posts": posts
    }
    return render(request, "user_profile.html", context)
@login_required(login_url="user_login")
def user_settings(request):
    user = User.objects.get(username = request.user)
    categories = Category.objects.all()
    if request.method == "POST":
        print(request.FILES, request.POST)
        if user.profile_photo and request.POST.get("profile_photo") != '':
            user.profile_photo.delete()
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("index")

    form = UserEditForm(instance=user)
    context = {
        "form": form,
        "user": user,
        "categories": categories
    }
    return render(request, "user_settings.html", context)





