from shop.models import Product, Profile

class Cart():
	def __init__(self, request):
		self.session = request.session
		# Get request
		self.request = request
		# get current session key if it exists
		cart = self.session.get('session_key')

		# if yuo user is new, no session key! Create one!
		if 'session_key' not in request.session:
			cart = self.session['session_key'] = {}


		# make sure cart is available on all pages of site
		self.cart = cart

	def db_add(self, product, quantity):
		product_id = str(product)
		product_qty = str(quantity)
		# logic
		if product_id in self.cart:
			pass
		else:
			# self.cart[product_id] = {'price': str(product.price)}
			self.cart[product_id] = int(product_qty)
		
		self.session.modified = True
		# Deal with logged in user
		if self.request.user.is_authenticated:
			# Get current user profile
			current_user = Profile.objects.filter(user__id=self.request.user.id)
			# Convert
			carty = str(self.cart)
			carty = carty.replace("\'", "\"")
			# save carty to profile model
			current_user.update(old_cart=str(carty))

	def add(self, product, quantity):
		product_id = str(product.id)
		product_qty = str(quantity)
		# logic
		if product_id in self.cart:
			pass
		else:
			# self.cart[product_id] = {'price': str(product.price)}
			self.cart[product_id] = int(product_qty)
		
		self.session.modified = True
		# Deal with logged in user
		if self.request.user.is_authenticated:
			# Get current user profile
			current_user = Profile.objects.filter(user__id=self.request.user.id)
			# Convert
			carty = str(self.cart)
			carty = carty.replace("\'", "\"")
			# save carty to profile model
			current_user.update(old_cart=str(carty))

	def cart_total(self):
		# get product ids
		product_ids = self.cart.keys()
		# look up keys in our products database model
		products = Product.objects.filter(id__in=product_ids)
		# get quantities
		quantities = self.cart
		# start counting at 0
		total = 0
		for key, value in quantities.items():
			key = int(key)
			for product in products:
				if product.id == key:
					total = total + (product.price * value)
		return total



	def __len__(self):
		return len(self.cart)

	def get_prods(self):
		# get ids from cart
		product_ids = self.cart.keys()
		# use ids to look up products in db model
		products = Product.objects.filter(id__in=product_ids)
		return products

	def get_quants(self):
		quantities = self.cart
		return quantities

	def update(self, product, quantity):
		product_id = str(product)
		product_qty = int(quantity)

		ourcart = self.cart
		ourcart[product_id] = product_qty

		self.session.modified = True

		# Deal with logged in user
		if self.request.user.is_authenticated:
			# Get current user profile
			current_user = Profile.objects.filter(user__id=self.request.user.id)
			# Convert
			carty = str(self.cart)
			carty = carty.replace("\'", "\"")
			# save carty to profile model
			current_user.update(old_cart=str(carty))
		thing = self.cart
		return thing

	def delete(self, product):
		product_id = str(product)
		# delete from dictionary
		if product_id in self.cart:
			del self.cart[product_id]

		self.session.modified = True 

		# Deal with logged in user
		if self.request.user.is_authenticated:
			# Get current user profile
			current_user = Profile.objects.filter(user__id=self.request.user.id)
			# Convert
			carty = str(self.cart)
			carty = carty.replace("\'", "\"")
			# save carty to profile model
			current_user.update(old_cart=str(carty))