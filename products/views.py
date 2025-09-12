from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from .forms import ProductForm

BASE_URL = "https://api.escuelajs.co/api/v1/"

def get_all_categories():
    """Helper function to fetch all categories from the API."""
    try:
        response = requests.get(f'{BASE_URL}categories')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching categories: {e}")
        return None

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
        response.raise_for_status()
        products = response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        products = []
        messages.error(request, f"Error al cargar productos: {e}")

    categories = get_all_categories()
    if categories is None:
        messages.error(request, "Error al cargar categorías.")
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
        messages.error(request, f"Error al cargar el detalle del producto: {e}")
    
    return render(request, 'products/product_detail.html', {'product': product})

def product_create(request):
    categories = get_all_categories()
    if categories is None:
        messages.error(request, "No se pueden cargar las categorías para crear un producto.")
        return redirect('product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, categories=categories)
        if form.is_valid():
            image_url = form.cleaned_data.get('image_url')

<<<<<<< HEAD
            # 1. Handle file upload if an image is provided
            if 'image' in request.FILES and request.FILES['image']:
=======
            if not image_url and 'image' in request.FILES:
>>>>>>> 862c37caab75b72e00a7267df5c9687689beefe5
                file = request.FILES['image']
                try:
                    upload_response = requests.post(f'{BASE_URL}files/upload', files={'file': file})
                    upload_response.raise_for_status()
                    image_url = upload_response.json().get('location')
                except requests.exceptions.RequestException as e:
                    form.add_error('image', f'Error al subir la imagen: {e}')

<<<<<<< HEAD
            # 2. Create product if image handling was successful
=======
>>>>>>> 862c37caab75b72e00a7267df5c9687689beefe5
            if not form.errors:
                images = [image_url] if image_url else ["https://via.placeholder.com/150"]
                
                payload = {
                    'title': form.cleaned_data['title'],
                    'price': float(form.cleaned_data['price']),
                    'description': form.cleaned_data['description'],
                    'categoryId': int(form.cleaned_data['categoryId']),
                    'images': images
                }
                
                try:
                    response = requests.post(f'{BASE_URL}products/', json=payload)
                    response.raise_for_status()
<<<<<<< HEAD
                    messages.success(request, "Producto creado exitosamente!")
                    return redirect('product_list')
                except requests.exceptions.RequestException as e:
                    print(f"Error creating product: {e}")
                    if e.response is not None:
                        print(f"API Response: {e.response.text}")
=======
                    messages.success(request, "¡Producto creado exitosamente!")
                    return redirect('product_list')
                except requests.exceptions.RequestException as e:
>>>>>>> 862c37caab75b72e00a7267df5c9687689beefe5
                    messages.error(request, f'Error al crear el producto: {e}')
                    form.add_error(None, f'Error al crear el producto: {e}')
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        form = ProductForm(categories=categories)
    
    return render(request, 'products/product_create.html', {'form': form})

def product_edit(request, pk):
    try:
        product_response = requests.get(f'{BASE_URL}products/{pk}')
        product_response.raise_for_status()
        product_data = product_response.json()
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error al cargar el producto para edición: {e}")
<<<<<<< HEAD
        return render(request, 'products/product_edit.html', {'error': f'Could not fetch product: {e}'})

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, is_edit=True)
        if form.is_valid():
            image_urls = product_data.get('images', [])
            
            # 1. Handle file upload if a new image is provided
            if 'image' in request.FILES and request.FILES['image']:
=======
        return redirect('product_list')

    categories = get_all_categories()
    if categories is None:
        messages.error(request, "No se pueden cargar las categorías para editar el producto.")
        return redirect('product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, categories=categories)
        if form.is_valid():
            image_urls = product_data.get('images', [])
            
            new_image_url = form.cleaned_data.get('image_url')
            if not new_image_url and 'image' in request.FILES:
>>>>>>> 862c37caab75b72e00a7267df5c9687689beefe5
                file = request.FILES['image']
                try:
                    upload_response = requests.post(f'{BASE_URL}files/upload', files={'file': file})
                    upload_response.raise_for_status()
                    new_image_url = upload_response.json().get('location')
                except requests.exceptions.RequestException as e:
                    form.add_error('image', f'Error al subir la imagen: {e}')
            
            if new_image_url:
                image_urls = [new_image_url]

            if not form.errors:
                payload = {
                    'title': form.cleaned_data['title'],
                    'price': float(form.cleaned_data['price']),
                    'description': form.cleaned_data['description'],
                    'categoryId': int(form.cleaned_data['categoryId']),
                    'images': image_urls
                }
                
                try:
                    response = requests.put(f'{BASE_URL}products/{pk}', json=payload)
                    response.raise_for_status()
<<<<<<< HEAD
                    messages.success(request, "Producto actualizado exitosamente!")
=======
                    messages.success(request, "¡Producto actualizado exitosamente!")
>>>>>>> 862c37caab75b72e00a7267df5c9687689beefe5
                    return redirect('product_list')
                except requests.exceptions.RequestException as e:
                    messages.error(request, f'Error al actualizar el producto: {e}')
                    form.add_error(None, f'Error al actualizar el producto: {e}')
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        initial_data = {
            'title': product_data.get('title'),
            'price': product_data.get('price'),
            'description': product_data.get('description'),
            'categoryId': product_data.get('category', {}).get('id'),
<<<<<<< HEAD
            'image_url': product_data.get('images', [None])[0]
        }
        form = ProductForm(initial=initial_data, is_edit=True)
=======
            'image_url': product_data.get('images', [''])[0]
        }
        form = ProductForm(initial=initial_data, categories=categories)
>>>>>>> 862c37caab75b72e00a7267df5c9687689beefe5
    
    return render(request, 'products/product_edit.html', {'form': form, 'product': product_data})

def product_delete(request, pk):
    if request.method == 'POST':
        try:
            response = requests.delete(f'{BASE_URL}products/{pk}')
<<<<<<< HEAD
            response.raise_for_status()  # Raise an exception for bad status codes
=======
            response.raise_for_status()
>>>>>>> 862c37caab75b72e00a7267df5c9687689beefe5
            messages.success(request, "Producto eliminado exitosamente!")
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            messages.error(request, f"Error al eliminar el producto: {e}")
    
    return redirect('product_list')