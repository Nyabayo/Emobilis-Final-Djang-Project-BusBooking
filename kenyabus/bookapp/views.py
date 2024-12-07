# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, Bus, Book
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.decorators import login_required
from decimal import Decimal

# Home page
def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return render(request, 'signin.html')

# Find bus page
@login_required(login_url='signin')
def findbus(request):
    context = {}

    if request.method == 'POST':
        source_r = request.POST.get('source')
        dest_r = request.POST.get('destination')
        date_r = request.POST.get('date')

        # Query the Bus model for buses matching the criteria
        bus_list = Bus.objects.filter(source=source_r, dest=dest_r, date=date_r)

        if bus_list.exists():
            context['bus_list'] = bus_list
            return render(request, 'list.html', context)
        else:
            context['error'] = "Sorry, no buses available for your search."
            return render(request, 'findbus.html', context)

    return render(request, 'findbus.html')

# Booking page
@login_required(login_url='signin')
def bookings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('bus_id')
        seats_r = int(request.POST.get('no_seats'))
        bus = get_object_or_404(Bus, id=id_r)

        if bus.rem >= seats_r:
            name_r = bus.bus_name
            cost = seats_r * bus.price
            source_r = bus.source
            dest_r = bus.dest
            nos_r = Decimal(bus.nos)
            price_r = bus.price
            date_r = bus.date
            time_r = bus.time
            username_r = request.user.username
            email_r = request.user.email
            userid_r = request.user.id
            rem_r = bus.rem - seats_r

            if rem_r >= 0:
                Bus.objects.filter(id=id_r).update(rem=rem_r)
                book = Book.objects.create(
                    name=username_r, email=email_r, userid=userid_r, bus_name=name_r,
                    source=source_r, busid=id_r, dest=dest_r, price=price_r, nos=seats_r,
                    date=date_r, time=time_r, status='BOOKED'
                )
                context["success"] = "Booking successful!"
            else:
                context["error"] = "Sorry, not enough seats available."
            return render(request, 'bookings.html', context)
        else:
            context["error"] = "Sorry, select fewer number of seats."
            return render(request, 'findbus.html', context)
    else:
        return render(request, 'findbus.html')

# Cancellation page
@login_required(login_url='signin')
def cancellings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('bus_id')
        book = get_object_or_404(Book, id=id_r)
        bus = get_object_or_404(Bus, id=book.busid)
        rem_r = bus.rem + book.nos
        Bus.objects.filter(id=book.busid).update(rem=rem_r)
        Book.objects.filter(id=id_r).update(status='CANCELLED', nos=0)
        return redirect(seebookings)
    else:
        return render(request, 'findbus.html')

# View booked buses
@login_required(login_url='signin')
def seebookings(request):
    context = {}
    id_r = request.user.id
    book_list = Book.objects.filter(userid=id_r)
    if book_list:
        return render(request, 'booklist.html', locals())
    else:
        context["error"] = "Sorry, no buses booked."
        return render(request, 'findbus.html', context)

# Sign up page
def signup(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        email_r = request.POST.get('email')
        password_r = request.POST.get('password')
        user = AuthUser.objects.create_user(name_r, email_r, password_r)
        if user:
            login(request, user)
            return render(request, 'thank.html')
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'signup.html', context)
    else:
        return render(request, 'signup.html', context)

# Sign in page
def signin(request):
    if request.user.is_authenticated:
        return redirect('home')

    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        password_r = request.POST.get('password')
        user = authenticate(request, username=name_r, password=password_r)
        if user:
            login(request, user)
            context["user"] = name_r
            context["id"] = request.user.id
            return render(request, 'success.html', context)
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'signin.html', context)
    else:
        context["error"] = "You are not logged in"
        return render(request, 'signin.html', context)

# Log out page
def signout(request):
    logout(request)
    context = {'error': "You have been logged out"}
    return render(request, 'signin.html', context)

# Success page after login
def success(request):
    context = {'error': "Login Successful!"}
    return render(request, 'success.html', context)
