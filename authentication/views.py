from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from election import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token

# Create your views here.
def home(request):
    return render(request, "authentication/index.html")

def signup(request):
    if request.method =="POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exists!! Please try some other username")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request, "Email address already registered")
            return redirect('home')

        if len(username)>11:
            messages.error(request, "Username must be under 11 charecters")
            return redirect('home')

        if pass1 != pass2:
            messages.error(request, "Passwords mismatch!!")
            return redirect('home')

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!")
            return redirect('home')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        #myuser.is_activate = False
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Your Account Has Been Successfully Created. We have sent you a confirmation email, please confirm")

        #welcome page
        subject = "Welcome to Election Commision RAIT!!"
        message = "Hello" + myuser.first_name + "!! \n" + "Welcome to Election Commision RAIT \n we have sent you a confirmation email, please confirm your email address in order to activate your account. \n\n Thanking You!"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        #email confirmation
        current_site = get_current_site(request)
        email_subject = "confirm your email @ Election Commision Login"
        message2 = render_to_string('email_confirmation.html',{

            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_siilently = True
        email.send()
        
        return redirect('signin')


    return render(request, "authentication/signup.html")


def activate(request,uid64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    
    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_activate = True
        #user.profile.signup_confirmation = True
        myuser.save()
        login(request, myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "authentication/index.html", {"fname":fname})

        else:
            messages.error(request,"Wrong Credentials")
            return redirect('home')

    return render(request, "authentication/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')

