from django.urls import path
from .views import *
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product_detail/<slug>/', ProductDetailView.as_view(), name='product-detail'),
    path("add-to-cart-<int:pro_id>/", AddToCartView.as_view(), name="addtocart"),
    path("my-cart/", MyCartView.as_view(), name="mycart"),
    path("managecart/<int:cartproduct_id>/", MyCartManage.as_view(), name="managecart"),
    path("empty-cart/", EmptyCartView.as_view(), name="emptycart"),

    path("checkout/", CheckOutView.as_view(), name="checkout"),
    path("login/", CustomerLoginView.as_view(), name="customerlogin"),
    path("logout/", CustomerLogoutView.as_view(), name="customerlogout"),
    path("register/", CustomerRegisterView.as_view(), name="customerregister"),
    path("allproducts/", AllProductsView.as_view(), name="allproducts"),
    path("profile/", CustomerProfileView.as_view(), name="customerprofile"),
    path("profile/order-<int:pk>/",CustomerOrderDetailView.as_view(), name="customerorderdetail"),
    path("search/", SearchView.as_view(), name="search"),
    path("add-comment/<slug>/", addCommentView, name="add-comment"),

    path("storekeeper-home/", StoreKeeperHomeView.as_view(), name="storekeeperhome"),
    path("storekeeper-all-orders/", StoreKeeperOrderListView.as_view(), name="storekeeperallorders"),
    path("storekeeper-all-products/", StoreKeeperProductListView.as_view(), name="storekeeperallproducts"),
    path("storekeeper-order-detail-<int:ord_id>/", StoreKeeperOrderDetailView.as_view(), name="storekeeperorderdetail"),
    path("storekeeper-order-<int:pk>-change/",
         StoreKeeperOrderStatuChangeView.as_view(), name="storekeeperorderstatuschange"),
    path("storekeeper-create-new-product/", StoreKeeperProductCreateView.as_view(), name="storekeepercreate"),
    path("storekeeper-login/", StoreKeeperLoginView.as_view(), name="storekeeperlogin"),
    
]
