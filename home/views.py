from re import template
from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from django.views.generic import TemplateView,ListView, CreateView, FormView, DetailView
from django.contrib.auth import authenticate, login, logout
from .forms import *
from .models import *
from django.urls import reverse_lazy, reverse
from django.db.models import Q

class Dispatch_class(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


class HomeView(Dispatch_class, View):
    def get(self, request):
        products = Product.objects.all()
        cart_id = request.session.get("cart_id")
        cartItems = 0
        if cart_id:
            cart = Cart.objects.get(id = cart_id)
            list_pro = CartProduct.objects.filter(cart = cart)
            cartItems = len(list_pro)
        context = {'products':products, 'cartItems': cartItems}

        return render(request, 'home.html', context)

class ProductDetailView(Dispatch_class,TemplateView):
    template_name = 'productdetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        product = Product.objects.get(slug = url_slug)
        product.view_count +=1
        product.save()
        context['product'] = product
        comments = Comment.objects.filter(product = product)
        context['comments'] = comments
        cart_id = self.request.session.get("cart_id")

        if cart_id:
            cart = Cart.objects.get(id = cart_id)
            list_pro = CartProduct.objects.filter(cart = cart)
            cartItems = len(list_pro)
            context['cartItems'] = cartItems
        return context 


class AddToCartView(Dispatch_class,TemplateView):
    template_name = "addtocart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs['pro_id']
        # get product
        product_obj = Product.objects.get(id=product_id)

        # check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            print(cart_id)
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(
                product=product_obj)
            # item already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.price.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.price.selling_price
                cart_obj.save()
            # new item is added in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, price=product_obj.price.selling_price, quantity=1, subtotal=product_obj.price.selling_price)
                cart_obj.total += product_obj.price.selling_price
                cart_obj.save()
        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, price=product_obj.price.selling_price, quantity=1, subtotal=product_obj.price.selling_price)
            cart_obj.total += product_obj.price.selling_price
            cart_obj.save()
        return context

class MyCartView(Dispatch_class,TemplateView):
    template_name = "cart.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            list_pro = CartProduct.objects.filter(cart = cart)
            cartItems = len(list_pro)
            context['cartItems'] = cartItems
        else:
            cart = None
        context['cart'] = cart
        return context

class MyCartManage(Dispatch_class,View):
    def get(self, request, *args, **kwargs):
        cartproduct_id = self.kwargs["cartproduct_id"]
        action = request.GET.get("action")
        cartProduct = CartProduct.objects.get(id=cartproduct_id)
        cart = cartProduct.cart
        print(action)
        if action == "add":
            cartProduct.quantity += 1
            cartProduct.subtotal += cartProduct.price
            cartProduct.save()
            cart.total += cartProduct.price
            cart.save()
        elif action == "sub":
            cartProduct.quantity -= 1
            cartProduct.subtotal -= cartProduct.price
            cartProduct.save()
            cart.total -= cartProduct.price
            cart.save()
            if cartProduct.quantity == 0:
                cartProduct.delete()

        elif action == "remove":
            cart.total -= cartProduct.subtotal
            cart.save()
            cartProduct.delete()
        else:
            pass
        return redirect("mycart")

class EmptyCartView(Dispatch_class,View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("mycart")


class CheckOutView(Dispatch_class,CreateView):
    template_name = 'checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id = cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            customer = self.request.user.customer
            form.instance.customer = customer
            form.instance.lastname = customer.lastname
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            form.instance.cart = cart
            form.instance.subtotal = cart.total
            form.instance.discount = 0
            form.instance.total = cart.total
            form.instance.order_status = "Order Received"
            status = "Order Received"
            order_statusObj = OrderStatus.objects.get(order_status = status)
            form.instance.order_statusID = order_statusObj
            pay_method = form.cleaned_data['payment_method']
            if pay_method == "Credit" or pay_method == "E-Wallet":
                form.instance.payment_completed = True
            payment_method = PaymentMethod.objects.get(payment_method = pay_method)
            form.instance.payment_methodID = payment_method
            del self.request.session['cart_id']
            order = form.save()
            shipping_address = Address(customer = customer, order = order, address = address,
            city = city, state = state, zipcode = zipcode)
            shipping_address.save()
        else:
            return redirect("home")
        return super().form_valid(form)


class CustomerLoginView(FormView):
    template_name = "customerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data["password"]
        user = authenticate(username=username, password=password)
        if user is not None and Customer.objects.filter(user=user).exists():
            login(self.request, user)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})

        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url

class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home")


class CustomerRegisterView(CreateView):
    template_name = "customerregister.html"
    form_class = CustomerRegisterForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        firstname = form.cleaned_data.get("firstname")
        lastname = form.cleaned_data.get("lastname")
        mobile = form.cleaned_data.get("mobile")
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        full_name = FullName.objects.create(firstname = firstname, lastname = lastname)
        full_name.save()
        form.instance.full_name = full_name
        form.instance.mobile = mobile
        form.instance.lastname = lastname
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class AllProductsView(TemplateView):
    template_name='home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        action = self.request.GET.get("action")
        
        if action == "book":
            category = Category.objects.get(title = "Book")
            books = Product.objects.filter(category = category)
            context["products"] = books
            return context 
        if action == "clothes":
            category = Category.objects.get(title = "Clothes")
            clothes = Product.objects.filter(category = category)
            context["products"] = clothes
            return context 
        if action == "electronic":
            category = Category.objects.get(title = "Electronic")
            electronics = Product.objects.filter(category = category)
            context["products"] = electronics
            return context

class CustomerProfileView(TemplateView):
    template_name = "customerprofile.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        # carts = Cart.objects.filter(customer = customer)
        # orders = [Order.objects.get(cart = cart) for cart in carts]
        # print('1')
        print(orders)
        context["orders"] = orders
        return context

# class CustomerOrderDetailView(DetailView):
#     template_name = "customerorderdetail.html"
#     model = Order
#     context_object_name = "ord_obj"

#     def dispatch(self, request, *args, **kwargs):
#         if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
#             order_id = self.kwargs["pk"]
#             order = Order.objects.get(id=order_id)
#             if request.user.customer != order.cart.customer:
#                 return redirect("customerprofile")
#         else:
#             return redirect("/login/?next=/profile/")
#         return super().dispatch(request, *args, **kwargs)

class CustomerOrderDetailView(TemplateView):
    template_name = "customerorderdetail.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect("customerprofile")
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs["pk"]
        order = Order.objects.get(id=order_id)
        address = Address.objects.get(order = order)
        context["ord_obj"]  = order
        context["address"] = address
        return context

class SearchView(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        results = Product.objects.filter(
            Q(title__icontains=kw) | Q(description__icontains=kw))
        print(results)
        context["results"] = results
        return context

def addCommentView(request, slug):
    url = request.META.get('HTTP_REFERER')
    print(slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            data = Comment()
            data.title = form.cleaned_data['title']
            data.comment = form.cleaned_data['comment']
            data.rate = form.cleaned_data['rate']
            print(data.rate)
            customer = request.user.customer
            print(customer)
            product = Product.objects.get(slug = slug)
            data.customer = customer
            data.product = product
            data.save()
            return redirect(url) 
    return redirect(url)

class StoreKeeperLoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and StoreKeeper.objects.filter(user=request.user).exists():
            print(StoreKeeper.objects.filter(user=request.user).exists())
        else:
            return redirect("/storekeeper-login/")
        return super().dispatch(request, *args, **kwargs)

class StoreKeeperLoginView(FormView):
    template_name = "storekeeper/storekeeperlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("storekeeperhome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and StoreKeeper.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credentials"})
        return super().form_valid(form)

class StoreKeeperHomeView(StoreKeeperLoginRequiredMixin, TemplateView):
    template_name = "storekeeper/storekeeperhome.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.filter(
            order_status="Order Received").order_by("-id")
        return context

class StoreKeeperOrderListView(StoreKeeperLoginRequiredMixin, ListView):
    template_name = "storekeeper/storekeeperorderlist.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorders"

class StoreKeeperProductListView(StoreKeeperLoginRequiredMixin, ListView):
    template_name = "storekeeper/storekeeperproductlist.html"
    queryset = Product.objects.all().order_by("-id")
    context_object_name = "allproducts"

class StoreKeeperOrderDetailView(StoreKeeperLoginRequiredMixin, TemplateView):
    template_name = 'storekeeper/storekeeperorderdetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ord_id = self.kwargs['ord_id']
        order = Order.objects.get(id = ord_id)
        shipping_address = Address.objects.get(order = order)
        context['order'] = order
        context['shipping_address'] = shipping_address
        context["allstatus"] = ORDER_STATUS
        return context

class StoreKeeperOrderStatuChangeView(StoreKeeperLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
        order_obj.order_status = new_status
        order_obj.save()
        return redirect("storekeeperallorders")

class StoreKeeperProductCreateView(StoreKeeperLoginRequiredMixin, CreateView):
    template_name = "storekeeper/storekeeperproductcreate.html"
    form_class = ProductForm
    success_url = reverse_lazy("storekeeperallproducts")

    def form_valid(self, form):
        marked_price = form.cleaned_data['marked_price']
        selling_price = form.cleaned_data['selling_price']
        warranty = form.cleaned_data['warranty']
        return_policy = form.cleaned_data['return_policy']
        price = Price.objects.create(marked_price = marked_price, selling_price = selling_price)
        warrantyObj = Warranty.objects.create(warranty = warranty, return_policy = return_policy)
        form.instance.price = price
        form.instance.warranty = warrantyObj
        p = form.save()
        
        return super().form_valid(form)