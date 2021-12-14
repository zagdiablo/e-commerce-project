from django.shortcuts import render
from django.http import JsonResponse
import json
from rest_framework.decorators import api_view
from .models import *


def store(request):
    loggedin = request.user.is_authenticated

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    contex = {"products":products, 'cartItems':cartItems, 'loggedin':loggedin}
    return render(request, "onlinestore/store.html", contex)

def cart(request):
    loggedin = request.user.is_authenticated

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = 0

    contex = {'items':items, 'order':order, 'cartItems':cartItems, 'loggedin':loggedin}
    return render(request, "onlinestore/cart.html", contex)

def checkout(request):
    loggedin = request.user.is_authenticated

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}

    contex = {'items':items, 'order':order, 'loggedin':loggedin}
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