from django.shortcuts import render, redirect
from .models import Product, Profile
from cart.cart import Cart
from payment.models import ShippingAddress
from payment.forms import ShippingForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UserInfoForm, ProductForm
from django import forms
import json

# Create your views here.
def index(request):
	products = Product.objects.all()
	return render(request, "index.html", { 'products':products })


def add_product(request):
    user = request.user
    if user.is_superuser:
        if request.method == 'POST':
            product_form = ProductForm(request.POST, request.FILES)         
            if product_form.is_valid():
                # save product to db
                product = product_form.save()
                return redirect('index')
            else:
                return render(request, 'add_product.html', { 'product_form': product_form })
        else:
            product_form = ProductForm()
            return render(request, 'add_product.html', { 'product_form': product_form })
    else:
        return redirect('index')


def product(request, pk):
	product = Product.objects.get(id=pk)
	return render(request, 'product.html', {'product':product})


def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			# Do some shopping cart stuff
			current_user = Profile.objects.get(user__id=request.user.id)
			# get saved cart
			saved_cart = current_user.old_cart
			# convert db string to python dictionary
			if saved_cart:
				converted_cart = json.loads(saved_cart)
				# add loaded dictionary to session
				cart = Cart(request)
				# loop through cart and add items from the db
				for key,value in converted_cart.items():
					cart.db_add(product=key, quantity=value)

			messages.success(request, ('You have been logged in!'))
			return redirect('index')
		else: 
			messages.error(request, ('There was an error logging in, try again'))
			return redirect('login')
	else: 
		return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request,('You have been logged out... Thanks for stopping by.'))
    return redirect('index')

def register_user(request):
	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			# log in user
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, ('User profile created! Please fill out your shipping details below.'))
			return redirect('update_info')
		else:
			messages.error(request, ('Whoops! There was a problem with your details. Please try again!'))
			return redirect('register')
	else:
		return render(request, 'register.html', {'form':form})
	

def update_info(request):
	if request.user.is_authenticated:
		current_user =Profile.objects.get(user__id=request.user.id)
		shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		form = UserInfoForm(request.POST or None, instance=current_user)
		shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

		if form.is_valid() or shipping_form.is_valid():
			form.save()
			shipping_form.save()
			messages.success(request, ('Your info has been updated'))
			return redirect('index')
		return render(request, 'update_info.html', {'form':form, 'shipping_form':shipping_form})
	else:
		messages.error(request, ('You must be logged in to access that page'))
		return redirect('index')	
