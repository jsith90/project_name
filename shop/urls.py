from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('product/<int:pk>', views.product, name='product'),
    path('add_product/', views.add_product, name='add_product'),
    path('update_info/', views.update_info, name='update_info'),
]
