from django import forms

class ProductForm(forms.Form):
    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    price = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    categoryId = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    images = forms.URLField(widget=forms.URLInput(attrs={'class': 'form-control'}))