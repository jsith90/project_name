from django.contrib import admin
from .models import Product, Profile
from django.contrib.auth.models import User

# Register your models here.
admin.site.register(Product)
admin.site.register(Profile)

# Mix profile info and user info
class ProfileInline(admin.StackedInline):
	model = Profile

# extend user model
class UserAdmin(admin.ModelAdmin):
	model = User
	field = ['username', 'first_name', 'last_name', 'email']
	inlines = [ProfileInline]

# Unregister old way
admin.site.unregister(User)

# reregister the new way
admin.site.register(User, UserAdmin)