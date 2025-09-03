from django.shortcuts import render, redirect
import requests
from .forms import ProductForm

BASE_URL = "https://api.escuelajs.co/api/v1/"

def product_list(request):
    search_query = request.GET.get('q')
    if search_query:
        # Assuming the API supports filtering by title
        response = requests.get(f'{BASE_URL}products?title={search_query}')
    else:
        response = requests.get(f'{BASE_URL}products')
    products = response.json()
    return render(request, 'products/product_list.html', {'products': products})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            payload = {
                'title': form.cleaned_data['title'],
                'price': form.cleaned_data['price'],
                'description': form.cleaned_data['description'],
                'categoryId': form.cleaned_data['categoryId'],
                'images': [form.cleaned_data['images']]
            }
            
            response = requests.post(f'{BASE_URL}products/', json=payload)
            
            if response.status_code == 201:
                return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'products/product_create.html', {'form': form})

def product_detail(request, product_id):
    response = requests.get(f'{BASE_URL}products/{product_id}')
    product = response.json()
    return render(request, 'products/product_detail.html', {'product': product})