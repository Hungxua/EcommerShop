from django import forms
from .models import *

class CheckoutForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput())
    city = forms.CharField(widget=forms.TextInput())
    state = forms.CharField(widget=forms.TextInput()) 
    zipcode = forms.CharField(widget=forms.TextInput())    
    class Meta:
        model = Order
        fields = ["payment_method"]

class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())

class CustomerRegisterForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput())
    firstname = forms.CharField(widget=forms.TextInput())
    lastname = forms.CharField(widget=forms.TextInput())
    class Meta:
        model = Customer
        fields = ["username", "password", "email","mobile" , "firstname", "lastname"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Customer with this username already exists.")

        return username

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields= ['title', 'comment', 'rate']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["title", "slug", "category", "image","description"]
    marked_price = forms.CharField(widget=forms.TextInput())
    selling_price = forms.CharField(widget=forms.TextInput())
    warranty = forms.CharField(widget=forms.TextInput())
    return_policy = forms.CharField(widget=forms.TextInput())
        