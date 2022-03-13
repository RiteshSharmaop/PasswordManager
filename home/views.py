from django.contrib.auth.models import User
from django.shortcuts import render , redirect
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate , login ,logout
import random
from django.core.mail import send_mail
# from PasswordManager.settings import EMAIL_HOST, EMAIL_HOST_USER
# from cryptography.fernet import Fernet
from cryptography.fernet import Fernet
from home.models import Password
from mechanize import Browser
import favicon
from .models import Password

br=Browser()
br.set_handle_robots(False)
fernet = Fernet(settings.KEY)



# Create your views here.
def home(request):
    if request.method == "POST":
        if "signup-form" in request.POST:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            password2 = request.POST.get("password2")
            
        



            #if password is not correct 
            # if user not exist or not identical
            if password != password2:
                mess="Enter Correct Password"
                messages.error(request,mess)
                return HttpResponseRedirect(request.path)
            #if password is correct
            # if username exists
            elif User.objects.filter(username=username).exists():
                mess=f"{username} already exists!"
                messages.error(request,mess)
                return HttpResponseRedirect(request.path)

            # if email exists
            elif User.objects.filter(email=email).exists():
                mess=f"{email} already exists!"
                messages.error(request,mess)
                return HttpResponseRedirect(request.path)
            
            else:
                User.objects.create_user(username,email,password)
                newuser=authenticate(request, username=username, password=password2)
                if newuser is not None:
                    login(request,newuser)
                    mess=f"{username}. Thanks for Joining"
                    messages.success(request,mess)
                    return HttpResponseRedirect(request.path)

        elif "logout" in request.POST:
            mess=f"{request.user}. You're Log-Out"
            logout(request)
            messages.success(request,mess)
            return HttpResponseRedirect(request.path)


        elif 'login-form' in request.POST:
            username = request.POST.get("username")
            password = request.POST.get("password")
            new_login = authenticate(request, username=username, password=password)
            if new_login is None:
                mss = f"Login failed! Make sure you're using the right account."
                messages.error(request, mss)
                return HttpResponseRedirect(request.path)
            else:
                code = str(random.randint(100000, 999999))
                global global_code
                global_code = code
                send_mail(
                    "Django Password Manager: confirm email",
                    f"Your verification code is {code}.",
                    settings.EMAIL_HOST_USER,
                    [new_login.email],
                    fail_silently=False,
                )
                return render(request, "home.html", {
                    "code":code, 
                    "user":new_login,
                })

        elif "confirm" in request.POST:
            input_code = request.POST.get("code")
            user =request.POST.get("user")
            if input_code != global_code:
                mss = f"{input_code} is Worng. Make sure you have Entered correct OTP!!!"
                messages.error(request, mss)
                return HttpResponseRedirect(request.path)
            else:
                login(request, User.objects.get(username=user))
                mss = f"{request.user} Welcome"
                messages.success(request, mss)
                return HttpResponseRedirect(request.path)

        elif "add-password" in request.POST:
            url = request.POST.get("url")
            email = request.POST.get("email")
            password = request.POST.get("password")
            #ecrypt data
            encrypted_email = fernet.encrypt(email.encode())
            encrypted_password = fernet.encrypt(password.encode())
            #get title of the website
            try:
                br.open(url)
                title = br.title()
            except:
                title = url
            #get logo url
            # try:
            # icon = favicon.get(url)[0].url
            # except:
                # icon = "https://cdn-icons-png.flaticon.com/128/1006/1006771.png"
            #print data
            # print("\n\n\n")
            # print(encrypted_email)
            # print(encrypted_password)
            # print(title)
            # print(icon)

    #         #save data in database
            new_password = Password.objects.create(
                user=request.user,
                name=title,
                # logo=icon,
                email=encrypted_email.decode(),
                password=encrypted_password.decode(),
            )

            mss = f"{title} is added successfully."
            messages.success(request, mss)
            return HttpResponseRedirect(request.path)

    context = {}
    if request.user.is_authenticated:
        passwords = Password.objects.all().filter(user=request.user)
        for password in passwords:
            password.email = fernet.decrypt(password.email.encode()).decode()
            password.password = fernet.decrypt(password.password.encode()).decode()
        context = {
            "passwords":passwords,
        }   



    return render(request, "home.html", context)