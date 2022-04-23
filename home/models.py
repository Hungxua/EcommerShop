from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class FullName(models.Model):
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    def __str__(self):
        return self.firstname + self.lastname

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.OneToOneField(FullName, on_delete=models.CASCADE)
    lastname = models.CharField(max_length=20)
    joined_on = models.DateTimeField(auto_now_add=True)
    mobile = models.CharField(max_length=10)
    def __str__(self):
        return self.lastname

class StoreKeeper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.OneToOneField(FullName, on_delete=models.CASCADE)
    lastname = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

class Category(models.Model):
    title = models.CharField(max_length=200)
    # slug = models.SlugField(unique=True)
    slug = models.SlugField(unique=True)
    def __str__(self):
        return self.title
    class Meta:
        unique_together = ('title', 'slug')

class Warranty(models.Model):
    warranty = models.CharField(max_length=300, null=True, blank=True)
    return_policy = models.CharField(max_length=300, null=True, blank=True)

class Price(models.Model):
    marked_price = models.PositiveIntegerField()
    selling_price = models.PositiveIntegerField(null=True, blank=True)

class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    warranty = models.ForeignKey(Warranty, on_delete= models.CASCADE)
    price = models.ForeignKey(Price, on_delete= models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products")
    description = models.TextField()
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Cart(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cart: " + str(self.id)

class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "Cart: " + str(self.cart.id) + " CartProduct: " + str(self.id)


METHOD = (
    ("Cash On Delivery", "Cash On Delivery"),
    ("Credit", "Credit"),
    ("E-Wallet", "E-Wallet"),
)
ORDER_STATUS = (
    ("Order Received", "Order Received"),
    ("Order Processing", "Order Processing"),
    ("On the way", "On the way"),
    ("Order Completed", "Order Completed"),
    ("Order Canceled", "Order Canceled"),
)

class OrderStatus(models.Model):
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS)
    description = models.CharField(max_length=100)
    def __str__(self):
        return self.order_status

class PaymentMethod(models.Model):
    payment_method = models.CharField(
        max_length=20, choices=METHOD, default="Cash On Delivery")
    description = models.CharField(max_length=100)
    def __str__(self):
        return self.payment_method

class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    # ordered_by = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer, on_delete= models.CASCADE)
    # shipping_address = models.CharField(max_length=200)
    lastname = models.CharField(max_length=20)
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    order_statusID = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_methodID = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    payment_method = models.CharField(
        max_length=20, choices=METHOD, default="Cash On Delivery")
    payment_completed = models.BooleanField(
        default=False, null=True, blank=True)

    def __str__(self):
        return "Order: " + str(self.id)

class Address(models.Model):
    customer= models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,null=True)
    address = models.CharField(max_length=200,null=False)
    city = models.CharField(max_length=200,null= False)
    state = models.CharField(max_length=200,null=False)
    zipcode = models.CharField(max_length=200,null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete= models.CASCADE)
    title = models.CharField(max_length= 50, blank= True)
    comment = models.CharField(max_length=250, blank=True)
    rate = models.IntegerField(default= 1)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
