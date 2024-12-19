import re
import logging
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.test import TestCase
from .models import User, Event, Submission
from .forms import SubmissionForm, CustomUserCreateForm, UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from PIL import Image
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.http import JsonResponse
from .utils import query_gemini_api
from .chatbot import ChatBot
# Create your views here.

def login_page(request):
    page = 'login'

    if request.method == "POST":
        user = authenticate(
            email=request.POST['email'],
            password=request.POST['password']
            )

        if user is not None:
            login(request, user)
            messages.info(request, 'You have succesfully logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Email OR Password is incorrect')
            return redirect('login')
    
    context = {'page':page}
    return render(request, 'login_register.html', context)

def register_page(request):
    form = CustomUserCreateForm()

    if request.method == 'POST':
        form = CustomUserCreateForm(request.POST, request.FILES,)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)
            messages.success(request, 'User account was created!')
            return redirect('home')
        else:
            messages.error(request, 'An error has occurred during registration')


    page = 'register'
    context = {'page':page, 'form':form}
    return render(request, 'login_register.html', context)

def logout_user(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('login')


def home_page(request):
    limit = request.GET.get('limit')

    if limit == None:
        limit = 20

    limit = int(limit)

    users = User.objects.filter(hackathon_participant=True)
    count = users.count()

    page = request.GET.get('page')
    paginator = Paginator(users, 50)

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        users = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        users = paginator.page(page)


    pages = list(range(1, (paginator.num_pages + 1)))
 

    
    events = Event.objects.all()
    context = {'users':users, 'events':events, 'count':count, 'paginator':paginator, 'pages':pages}
    return render(request, 'home.html', context)


def user_page(request, pk):
    user = User.objects.get(id=pk)
    context = {'user':user}
    return render(request, 'profile.html', context)

@login_required(login_url='/login')
def account_page(request):
    user = request.user

    context = {'user':user}
    return render(request, 'account.html', context)

@login_required(login_url='/login')
def edit_account(request):
    
    form = UserForm(instance=request.user)

    if request.method == 'POST':
        
        form = UserForm(request.POST, request.FILES,  instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            return redirect('account')

    context = {'form':form}
    return render(request, 'user_form.html', context)

@login_required(login_url='/login')
def change_password(request):   
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
       
        if password1 == password2:
             new_pass = make_password(password1)
             request.user.password = new_pass
             request.user.save()
             messages.success(request, 'You have succesfully reset your password!')
             return redirect('account')

    return render(request, 'change_password.html')


import time
from datetime import datetime

def event_page(request, pk):
    event = Event.objects.get(id=pk)
    
    
    registered = False
    submitted = False
    
    if request.user.is_authenticated:

        registered = request.user.events.filter(id=event.id).exists()
        submitted = Submission.objects.filter(participant=request.user, event=event).exists()
    context = {'event':event, 'registered':registered, 'submitted':submitted}
    return render(request, 'event.html', context)

def about_page(request):
    return render(request, 'about.html')

def contact_view(request):
    if request.method == "POST":
        # Handle form submission here
        pass
    return render(request, 'contact.html')


@login_required(login_url='/login')
def registration_confirmation(request, pk):
    event = Event.objects.get(id=pk)

    if request.method == 'POST':
        event.participants.add(request.user)
        return redirect('event', pk=event.id)

    
    return render(request, 'event_confirmation.html', {'event':event})

@login_required(login_url='/login')
def project_submission(request, pk):
    event = Event.objects.get(id=pk)

    form = SubmissionForm()

    if request.method == 'POST':
        form = SubmissionForm(request.POST)

        if form.is_valid():
            submission = form.save(commit=False)
            submission.participant = request.user
            submission.event = event
            submission.save()
            
            return redirect('account')

    context = {'event':event, 'form':form}
    return render(request, 'submit_form.html', context)


#Add owner authentication
@login_required(login_url='/login')
def update_submission(request, pk):
    submission = Submission.objects.get(id=pk)

    if request.user != submission.participant:
        return HttpResponse('You cant be here!!!!')

    event = submission.event
    form = SubmissionForm(instance=submission)

    if request.method == 'POST':
        form = SubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            return redirect('account')


    context = {'form':form, 'event':event}

    return render(request, 'submit_form.html', context)


from django.shortcuts import render

@login_required(login_url='/login')
def chatbot_page(request):
    """
    Renders the chatbot interface.
    """
    return render(request, 'chatbot.html')


#Add owner authentication
# Initialize conversation history
logger = logging.getLogger(__name__)

@login_required(login_url='/login')
def chatbot_interact(request):
    if "chatbot" not in request.session:
        chatbot = ChatBot()
        request.session["chatbot"] = chatbot.to_dict()
    else:
        chatbot = ChatBot.from_dict(request.session["chatbot"])

    if request.method == "POST":
        import json
        try:
            body = json.loads(request.body)
            user_message = body.get("prompt", "").strip()

            if user_message:
                print(f"User message: {user_message}")
                bot_message = chatbot.get_response(user_message)
                print(f"Bot response: {bot_message}")
                request.session["chatbot"] = chatbot.to_dict()
                logger.info(f"Response sent: {bot_message}")
                return JsonResponse({"response": bot_message})

            return JsonResponse({"response": "Error: Please enter a valid prompt."})
        except Exception as e:
            logger.error(f"Chatbot interaction error: {e}")
            return JsonResponse({"response": f"Error: {str(e)}"})
    chatbot.clear_history()
    request.session["chatbot"] = chatbot.to_dict()
    return JsonResponse({"response": "Chatbot ready to interact."})




