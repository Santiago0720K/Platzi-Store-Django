from django import forms
import requests

BASE_URL = "https://api.escuelajs.co/api/v1/"

class ProductForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del producto'}))
    price = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio (ej. 99.99)'})
    )
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción detallada del producto'}))
    categoryId = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'id': 'id_image_input', 'style': 'display: none;'}))
    image_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'O ingrese la URL de la imagen'}))

    def __init__(self, *args, categories=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = "Imagen del Producto"
        self.fields['image_url'].label = "URL de la Imagen (Opcional)"
        self.fields['categoryId'].label = "Categoría"

        if categories:
            self.fields['categoryId'].choices = [(c['id'], c['name']) for c in categories]
        else:
            self.fields['categoryId'].choices = []
            self.add_error(None, "No se pudieron cargar las categorías. Intente de nuevo más tarde.")
