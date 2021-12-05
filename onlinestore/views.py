from django.shortcuts import render


def store(request):
    contex = {}
    return render(request, "onlinestore/store.html", contex)

def cart(request):
    contex = {}
    return render(request, "onlinestore/cart.html", contex)

def checkout(request):
    contex = {}
    return render(request, "onlinestore/checkout.html", contex)