from django.shortcuts import render, redirect
from django.contrib import messages # Import messages
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
        messages.error(request, f"Error al cargar productos: {e}") # Add error message

    # Fetch categories
    try:
        categories_response = requests.get(f'{BASE_URL}categories')
        categories_response.raise_for_status()
        all_categories = categories_response.json()
        
        categories = all_categories
        
    except requests.exceptions.RequestException as e:
        print(f"API categories request failed: {e}")
        categories = []
        messages.error(request, f"Error al cargar categorías: {e}") # Add error message

    return render(request, 'products/product_list.html', {'products': products, 'categories': categories})

def product_detail(request, pk):
    try:
        response = requests.get(f'{BASE_URL}products/{pk}')
        response.raise_for_status()
        product = response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        product = None
        messages.error(request, f"Error al cargar el detalle del producto: {e}") # Add error message
    
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
                    form.add_error('image', f'Error al subir la imagen: {e}')

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
                    messages.success(request, "Producto creado exitosamente!") # Success message
                    return redirect('product_list')
                except requests.exceptions.RequestException as e:
                    print(f"Error creating product: {e}")
                    if e.response is not None:
                        print(f"API Response: {e.response.text}")
                    messages.error(request, f'Error al crear el producto: {e}') # Error message
                    form.add_error(None, f'Error al crear el producto: {e}')
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.") # Form validation error
    else:
        form = ProductForm()
    
    return render(request, 'products/product_create.html', {'form': form})

def product_edit(request, pk):
    try:
        product_response = requests.get(f'{BASE_URL}products/{pk}')
        product_response.raise_for_status()
        product_data = product_response.json()
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error al cargar el producto para edición: {e}") # Add error message
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
                    form.add_error('image', f'Error al subir la imagen: {e}')
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
                    messages.success(request, "Producto actualizado exitosamente!") # Success message
                    return redirect('product_list')
                except requests.exceptions.RequestException as e:
                    messages.error(request, f'Error al actualizar el producto: {e}') # Error message
                    form.add_error(None, f'Error al actualizar el producto: {e}')
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.") # Form validation error
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
            messages.success(request, "Producto eliminado exitosamente!") # Success message
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            messages.error(request, f"Error al eliminar el producto: {e}") # Error message
    
    return redirect('product_list')
