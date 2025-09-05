import requests
from django.core.management.base import BaseCommand
from products.models import Category, Product

class Command(BaseCommand):
    help = 'Fetches products and categories from the Platzi Fake Store API'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Fetching data from Platzi Fake Store API...'))

        # Fetch categories
        try:
            categories_response = requests.get('https://api.escuelajs.co/api/v1/categories')
            categories_response.raise_for_status()
            categories_data = categories_response.json()

            for category_data in categories_data:
                # The API can return invalid category data
                if 'id' not in category_data or 'name' not in category_data:
                    self.stdout.write(self.style.WARNING(f'Skipping invalid category data: {category_data}'))
                    continue

                category, created = Category.objects.update_or_create(
                    id=category_data['id'],
                    defaults={
                        'name': category_data['name'],
                        'image': category_data.get('image', '')
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Updated category: {category.name}'))

        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Error fetching categories: {e}'))
            return
        except ValueError: # Catches JSON decoding errors
            self.stderr.write(self.style.ERROR('Error decoding category JSON'))
            return


        # Fetch products
        try:
            products_response = requests.get('https://api.escuelajs.co/api/v1/products')
            products_response.raise_for_status()
            products_data = products_response.json()

            for product_data in products_data:
                # Basic validation for product data
                if not all(k in product_data for k in ['id', 'title', 'price', 'category']):
                    self.stdout.write(self.style.WARNING(f'Skipping invalid product data: {product_data}'))
                    continue
                
                # The API has some bad data where the category is not a dict
                if not isinstance(product_data.get('category'), dict) or 'id' not in product_data.get('category'):
                     self.stdout.write(self.style.WARNING(f'Skipping product with invalid category data: {product_data["title"]}'))
                     continue

                category_id = product_data['category']['id']
                try:
                    category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f'Category with id {category_id} does not exist. Skipping product: {product_data["title"]}'))
                    continue

                images = product_data.get('images', [])
                # The model expects a single image URL, so we'll take the first one.
                # Also, the API sometimes returns invalid image URLs in a list of strings.
                image_url = ''
                if images and isinstance(images, list) and len(images) > 0:
                    # A simple check to see if the item in the list is a string (URL)
                    if isinstance(images[0], str) and images[0].startswith('http'):
                        image_url = images[0]


                product, created = Product.objects.update_or_create(
                    id=product_data['id'],
                    defaults={
                        'title': product_data['title'],
                        'price': product_data['price'],
                        'description': product_data.get('description', ''),
                        'category': category,
                        'image': image_url,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created product: {product.title}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Updated product: {product.title}'))

        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Error fetching products: {e}'))
            return
        except ValueError:
            self.stderr.write(self.style.ERROR('Error decoding product JSON'))
            return

        self.stdout.write(self.style.SUCCESS('Data fetching complete.'))
