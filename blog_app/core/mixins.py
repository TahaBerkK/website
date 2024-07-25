from django.shortcuts import redirect


class LoginRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('page_not_found')
        return super().dispatch(request, *args, **kwargs)
         
class AuthorizationCheckMixin:
    
    def has_permission(self, post, request):
        user = request.user
        host = post.host
        if user == host:
            return True
        elif user.role == "manager":
            return True
        elif user.role == "teacher" and user.clas == host.clas:
            return True
        return False
        

