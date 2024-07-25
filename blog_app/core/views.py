from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.generic import View, ListView, FormView, DetailView, UpdateView, DeleteView, CreateView
from typing import Any
from .models import *
from .mixins import *
from .forms import UserEditForm, UserLoginForm, UserRegisterForm, PostForm


class IndexView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "index.html"
    paginate_by = 1
    context_object_name = "posts"
    
    def get_queryset(self):
        q = self.request.GET.get('q') if self.request.GET.get('q') != None else ''
        queryset = Post.objects.filter(Q(title__icontains = q)|
                                       Q(description__icontains = q)|
                                       Q(category__name__contains = q)|
                                       Q(host__username__contains = q)
                                    ).order_by("-created")
        if self.request.user.role == 'student':
            queryset = queryset.filter(host = self.request.user)
        return queryset
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "post_creation_edit.html"
    success_url = "/"

    def form_valid(self, form):
        form.instance.host = self.request.user        
        return super().form_valid(form)

class PostDetails(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "post_details.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["comments"] = Comment.objects.filter(post = context["post"])
        return context
    
    def post(self, request, pk):
        post = Post.objects.get(id=pk)
        content = request.POST.get("content") if request.POST.get("content") != '' else None
        if content != None:
            user = request.user
            new_comment = Comment.objects.create(user = user, content = content, post = post)
            new_comment.save()
            return redirect("post_details", pk = post.id)
        return redirect("post_details", pk = post.id)

class PostEdit(LoginRequiredMixin, AuthorizationCheckMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "post_creation_edit.html"
    success_url = "/"
    
    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')  # Get the pk from kwargs
        post = Post.objects.get(id=pk)
        
        if not self.has_permission(post, request):
            return redirect('page_not_found')  # Redirect if permission is denied

        return super().dispatch(request, *args, **kwargs)

class PostDelete(LoginRequiredMixin, AuthorizationCheckMixin, DeleteView):

    def get(self, request, pk):
        post = Post.objects.get(id=pk)
        if self.has_permission(post, request):
            post.delete()
        else:
            return redirect("404")

        return redirect("index")

class UserRegister(FormView):
    model = User
    form_class = UserRegisterForm
    template_name = "user_login_register.html"
    success_url = "/"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login"] = False
        return context

    def clean_username(self):
        username = self.request.POST.get('username')
        return username

    def clean_nickname(self):
        nickname = self.request.POST.get('nickname')
        return nickname
    
    def clean_email(self):
        email = self.request.POST.get('email')
        return email

    def clean_password(self):
        password = self.request.POST.get('password')
        return password

    def form_valid(self, form):
        username = self.clean_username()
        nickname = self.clean_nickname()
        email = self.clean_email()
        password = self.clean_password()
        if username and nickname and email and password is not '':
            user = User.objects.create_user(username = username, nickname = nickname, email = email, password = password)
            user.save()
        return super().form_valid(form)

class UserLogin(FormView):
    model = User
    form_class = UserLoginForm
    template_name = "user_login_register.html"
    success_url = "/"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login'] = True 
        return context
    
    def clean_username(self):
        username = self.request.POST.get('username')
        return username

    def clean_password(self):
        password = self.request.POST.get('password')
        return password
    
    def form_valid(self, form):
        username = self.clean_username()
        password = self.clean_password()
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            messages.error(self.request, "Username or Password incorrect")
            return super().form_valid(form) 

def UserLogout(request):
    logout(request)
    return redirect("index")

class UserProfile(LoginRequiredMixin, DetailView):
    model = User
    template_name = "user_profile.html"
    context_object_name = "user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["posts"] = Post.objects.filter(host=self.object)
        return context 

class UserSettings(LoginRequiredMixin, AuthorizationCheckMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = "user_settings.html"
    success_url = "/"
    slug_field = "username"
    slug_url_kwarg = "username"

    def has_permission(self, user):
        return self.request.user.role == "manager" or self.request.user == user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context

    def post(self, request, username):
        user = User.objects.get(username = username)
        if self.has_permission(user):
            if user.profile_photo and request.POST.get("profile_photo") != '':
                user.profile_photo.delete()
            form = UserEditForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                return redirect("index")

class StudentTable(LoginRequiredMixin, AuthorizationCheckMixin, ListView):
    model = User
    template_name = "student_table.html"
    context_object_name = "members"
    slug_field = "username"
    slug_url_kwarg = "username" 
    
    def has_permission(self, request):
        return request.user.role == "manager" or request.user.role == "teacher"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        queryset = context["members"]
        
        paginator = Paginator(queryset, 1)  # Show 25 contacts per page.
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj
        context["classes"] = Class.objects.all()
        if self.request.user.role == "teacher":
            context["classes"] = Class.objects.filter(id = self.request.user.clas.id)
        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        
        q = self.request.GET.get('q') if self.request.GET.get('q') != None else ''
        w = self.request.GET.get('w') if self.request.GET.get('w') != None else ''
        search = self.request.GET.get('search') if self.request.GET.get('search') != None else ''

        queryset = User.objects.all()
            
        if self.request.user.role == "teacher":
            queryset = queryset.filter(clas = self.request.user.clas, role = "student")
        
        if w != '' and self.request.user.role == "manager":
            queryset = User.objects.filter(role = w)
        
        if q != '':
            _class = Class.objects.get(id = q)
            queryset = queryset.filter(clas = _class)

        if search != '':
            queryset = queryset.filter(username__icontains = search)
        return queryset

class PageNotFound(View):
    def get(self, request):
        return render(request, "404.html")




'''
SPARE CODE IN CASES OF NEED:
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
'''




