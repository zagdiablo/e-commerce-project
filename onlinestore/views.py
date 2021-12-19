from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import json
import datetime
from rest_framework.decorators import api_view
from .models import *
from .utils import cookieCart, cartData, guestOrder
from .forms import CreateUserForm
# from .currencyConvert import Currency_convertor as cc #(untuk currency converter jika menggunakan paypal)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password = password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, "Username atau password salah")

    contex = {}
    return render(request, "onlinestore/login.html", contex)


def logoutUser(request):
    logout(request)
    return redirect('login')


def register(request):
    form = CreateUserForm()

    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f'Pendaftaran akun "{user}" berhasil, silahkan login')
            theUser = User.objects.get(username=request.POST.get('username'))
            Customer.objects.create(user=theUser, name=request.POST.get('username'), email=request.POST.get('email'))
            return redirect('login')

    contex = {'form':form}
    return render(request, "onlinestore/register.html", contex)


def store(request):
    loggedin = request.user.is_authenticated
    
    if loggedin:
        username = request.user.username
    else:
        username = 'Silahkan login/daftar'

    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    contex = {"products":products, 'cartItems':cartItems, 'loggedin':loggedin, 'username':username}
    return render(request, "onlinestore/store.html", contex)


def cart(request):
    loggedin = request.user.is_authenticated
    
    if loggedin:
        username = request.user.username
    else:
        username = 'Silahkan login/daftar'

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    contex = {'items':items, 'order':order, 'cartItems':cartItems, 'loggedin':loggedin, 'username':username}
    return render(request, "onlinestore/cart.html", contex)


def checkout(request):
    loggedin = request.user.is_authenticated
    
    if loggedin:
        username = request.user.username
    else:
        username = 'Silahkan login/daftar'
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    contex = {'items':items, 'order':order, 'loggedin':loggedin, 'username':username}
    return render(request, "onlinestore/checkout.html", contex)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('productId:', productId)
    print('action:', action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    print(f"total:{total} | {float(order.get_cart_total)}")

    if total == float(order.get_cart_total):
        order.complete = True
        order.donated_amount = total * 0.05
        order.profit = total * 0.10
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment complete', safe=False)
