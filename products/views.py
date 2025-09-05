from django.shortcuts import render, redirect
import requests
from .forms import ProductForm

BASE_URL = "https://api.escuelajs.co/api/v1/"

def product_list(request):
    search_query = request.GET.get('q')
    category_id = request.GET.get('category')
    url = f'{BASE_URL}products'
    
    params = {}
    if search_query:
        params['title'] = search_query
    if category_id:
        params['categoryId'] = category_id

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        products = response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        products = []

    # Fetch categories
    try:
        categories_response = requests.get(f'{BASE_URL}categories')
        categories_response.raise_for_status()
        all_categories = categories_response.json()
        
        # Filter categories to include only the desired ones
        desired_category_names = ["Clothes", "Furniture", "Electronics", "Shoes", "Miscellaneous"]
        categories = [cat for cat in all_categories if cat.get('name') in desired_category_names]
        
    except requests.exceptions.RequestException as e:
        print(f"API categories request failed: {e}")
        categories = []

    return render(request, 'products/product_list.html', {'products': products, 'categories': categories})

def product_detail(request, pk):
    try:
        response = requests.get(f'{BASE_URL}products/{pk}')
        response.raise_for_status()
        product = response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        product = None
    
    return render(request, 'products/product_detail.html', {'product': product})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            image_url = None
            # 1. Handle file upload if an image is provided
            if 'image' in request.FILES:
                file = request.FILES['image']
                try:
                    upload_response = requests.post(f'{BASE_URL}files/upload', files={'file': file})
                    upload_response.raise_for_status()
                    image_url = upload_response.json().get('location')
                except requests.exceptions.RequestException as e:
                    form.add_error('image', f'Error uploading image: {e}')

            # 2. Create product if image upload was successful (or no image was provided)
            if not form.errors:
                payload = {
                    'title': form.cleaned_data['title'],
                    'price': float(form.cleaned_data['price']),
                    'description': form.cleaned_data['description'],
                    'categoryId': form.cleaned_data['categoryId'],
                    'images': [image_url] if image_url else ["https://via.placeholder.com/150"]
                }
                
                try:
                    response = requests.post(f'{BASE_URL}products/', json=payload)
                    response.raise_for_status()
                    return redirect('product_list')
                except requests.exceptions.RequestException as e:
                    print(f"Error creating product: {e}")
                    if e.response is not None:
                        print(f"API Response: {e.response.text}")
                    form.add_error(None, f'Error creating product: {e}')
        else:
            pass
    else:
        form = ProductForm()
    
    return render(request, 'products/product_create.html', {'form': form})

def product_edit(request, pk):
    try:
        product_response = requests.get(f'{BASE_URL}products/{pk}')
        product_response.raise_for_status()
        product_data = product_response.json()
    except requests.exceptions.RequestException as e:
        return render(request, 'products/product_edit.html', {'error': f'Could not fetch product: {e}'})

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            image_urls = product_data.get('images', [])
            
            # 1. Handle file upload if a new image is provided
            if 'image' in request.FILES:
                file = request.FILES['image']
                try:
                    upload_response = requests.post(f'{BASE_URL}files/upload', files={'file': file})
                    upload_response.raise_for_status()
                    new_image_url = upload_response.json().get('location')
                    image_urls = [new_image_url] # Replace old images with the new one
                except requests.exceptions.RequestException as e:
                    form.add_error('image', f'Error uploading image: {e}')
            elif form.cleaned_data.get('image_url'):
                image_urls = [form.cleaned_data['image_url']]

            # 2. Update product if form is still valid
            if not form.errors:
                payload = {
                    'title': form.cleaned_data['title'],
                    'price': form.cleaned_data['price'],
                    'description': form.cleaned_data['description'],
                    'images': image_urls
                }
                
                try:
                    response = requests.put(f'{BASE_URL}products/{pk}', json=payload)
                    response.raise_for_status()
                    return redirect('product_list')
                except requests.exceptions.RequestException as e:
                    form.add_error(None, f'Error updating product: {e}')
    else:
        # Pre-populate the form with existing data
        initial_data = {
            'title': product_data.get('title'),
            'price': product_data.get('price'),
            'description': product_data.get('description'),
            'categoryId': product_data.get('category', {}).get('id'),
        }
        form = ProductForm(initial=initial_data)
    
    return render(request, 'products/product_edit.html', {'form': form, 'product': product_data})

def product_delete(request, pk):
    if request.method == 'POST':
        try:
            response = requests.delete(f'{BASE_URL}products/{pk}')
            response.raise_for_status()  # Raise an exception for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
    
    return redirect('product_list')
