from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import ShippingAddress, Order, OrderItem
from shop.models import Profile, Product
from django.contrib import messages
from django.contrib.auth.models import User
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import uuid #unique user id for duplicate orders
import stripe
from django.http import HttpResponse
from venv import logger
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
 

def not_shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=False, paid=True)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# get order
			order = Order.objects.filter(id=num)
			# Update the status
			now = datetime.datetime.now()
			order.update(shipped=True, date_shipped=now)

			messages.success(request, "Shipping Status Updated")
			return redirect('index')
			
		return render(request, 'payment/not_shipped_dash.html', {'orders':orders})
	else:
		messages.success(request, 'Access Denied.')
		return redirect('index')
	

def shipped_dash(request):
	if request.user.is_authenticated and request.user.is_superuser:
		orders = Order.objects.filter(shipped=True)
		if request.POST:
			status = request.POST['shipping_status']
			num = request.POST['num']
			# get order
			order = Order.objects.filter(id=num)
			# Update the status
			now = datetime.datetime.now()
			order.update(shipped=False)

			messages.success(request, "Shipping Status Updated")
			return redirect('index')

		return render(request, 'payment/shipped_dash.html', {'orders':orders})
	else:
		messages.success(request, 'Access Denied.')
		return redirect('index')


def orders(request, pk):
	if request.user.is_authenticated and request.user.is_superuser:
		# get the order
		order = Order.objects.get(id=pk)
		# get the order item
		items = OrderItem.objects.filter(order=pk)

		if request.POST:
			status = request.POST['shipping_status']
			# check if true or false
			if status == "true":
				# get the order
				order = Order.objects.filter(id=pk)
				# Update the status
				now = datetime.datetime.now()
				order.update(shipped=True, date_shipped=now)
			else:
				# get the order
				order = Order.objects.filter(id=pk)
				# Update the status
				order.update(shipped=False)

			messages.success(request, "Shipping Status Updated")
			return redirect('index')

		return render(request, 'payment/orders.html', {'order':order, 'items':items})
	else:
		messages.success(request, 'Access Denied.')
		return redirect('index')


def checkout(request):
	# get cart
	cart = Cart(request)
	cart_products = cart.get_prods
	quantities = cart.get_quants
	totals = cart.cart_total()
	
	if request.user.is_authenticated:
		# Check out as logged in user
		shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
		return render(request, 'payment/checkout.html', {'cart_products':cart_products, 'quantities':quantities, 'totals':totals, 'shipping_form':shipping_form})
	else:
		# Check out as guest
		shipping_form = ShippingForm(request.POST or None)
		return render(request, 'payment/checkout.html', {'cart_products':cart_products, 'quantities':quantities, 'totals':totals, 'shipping_form':shipping_form})



def billing_info(request):
    if request.method == 'POST':
        user = request.user
        cart = Cart(request)
        current_cart = cart.cart
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        # Save shipping information in the session
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address = (
            f"{my_shipping['shipping_address1']}\n"
            f"{my_shipping['shipping_address2']}\n"
            f"{my_shipping['shipping_city']}\n"
            f"{my_shipping['shipping_region']}\n"
            f"{my_shipping['shipping_postcode']}\n"
            f"{my_shipping['shipping_country']}"
        )

        if user.is_authenticated:
            # Retrieve or create Stripe customer
            if hasattr(user, 'profile') and user.profile.stripe_customer_id:
                customer_id = user.profile.stripe_customer_id
                customer = stripe.Customer.retrieve(customer_id)
            else:
                customer = stripe.Customer.create(
                    name=f"{user.first_name} {user.last_name}",
                    email=user.email,
                )
                user.profile.stripe_customer_id = customer.id
                user.profile.save()

        # Create a PaymentIntent
        items = [{'id': product.id, 'quantity': quantities()[str(product.id)]} for product in cart_products()]
        intent_data = {
            "amount": calculate_order_amount(request, items),
            "currency": "usd",
            "automatic_payment_methods": {"enabled": True},
            "receipt_email": email,
        }

        # Conditionally add customer to the intent data if it exists
        if user.is_authenticated and hasattr(customer, 'id'):
            intent_data["customer"] = customer.id

        # Create the PaymentIntent with the constructed data
        intent = stripe.PaymentIntent.create(**intent_data)

        # Create the order in the database
        create_order = Order(
            full_name=full_name, 
            email=email, 
            shipping_address=shipping_address, 
            amount_paid=totals,
			payment_intent_id=intent.id,
        )
        create_order.save()
        order_id = create_order.pk

        # Create order items
        for product in cart_products():
            product_id = product.id
            price = product.price
            quantity = quantities().get(str(product.id), 0)
            create_order_item = OrderItem(
                order_id=order_id, 
                product_id=product_id, 
                quantity=quantity, 
                price=price,
            )
            create_order_item.save()

            # Retrieve or create Stripe Product
            if hasattr(product, 'stripe_product_id') and product.stripe_product_id:
                stripe_product = stripe.Product.retrieve(product.stripe_product_id)
            else:
                stripe_product = stripe.Product.create(
                    name=product.name, 
                    default_price_data={
                        "unit_amount": int(product.price * 100),  # Convert to cents
                        "currency": "usd",
                    }
                )
                product.stripe_product_id = stripe_product.id
                product.save()

        return render(request, 'payment/billing_info.html', {
            'totals': totals,
            'current_cart': current_cart,
            'client_secret': intent.client_secret,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
            'cart_products': cart_products,
            'quantities': quantities,
            'shipping_info': request.POST
        })

    else:
        messages.error(request, 'Access Denied.')
        return redirect('index')



def calculate_order_amount(request, items):
	total_amount = 0
	cart = Cart(request)

	for item in items:
		product_id = item['id']
		quantity = item['quantity']
		product = Product.objects.get(id=product_id)
		price = product.price
		# Multiply price by quantity and add to the total amount
		total_amount += price * quantity
		# Return the total amount in the smallest currency unit (e.g., cence for USD)
	return int(total_amount * 100)  # Convert to cence if using USD


@csrf_exempt
def stripe_webhook(request):
	payload = request.body
	sig_header = request.META['HTTP_STRIPE_SIGNATURE']
	event = None

	try:
		event = stripe.Webhook.construct_event(
			payload, sig_header, endpoint_secret
		)
	except (ValueError, stripe.error.SignatureVerificationError) as e:
		return HttpResponse(status=400)
	# handle event
	if event['type'] in ['payment_intent.created', 'charge.succeeded', 'charge.updated']:
		return JsonResponse({'status': 'success'}, status=200)
	elif event['type'] == 'payment_intent.succeeded':
		payment_intent_id = event['data']['object']['id']
		my_order = Order.objects.get(payment_intent_id=payment_intent_id)
		my_order.paid = True
		my_order.save()
		return JsonResponse({'status': 'success'}, status=200)
	else:
		print(f'Unhandled event type: {event["type"]}')
		return HttpResponse(status=400)

# def customer(request):
# 	if request.method == 'POST':
# 		user = request.user
# 		try: 
# 			profile = stripe.Customer.create(
# 				name= user.first_name,
# 				email= user.email,
# 			)
# 			return JsonResponse({'customer_id': profile.id}, status=201)
# 		except Exception as e:
# 			return JsonResponse({'error': str(e)}, status=400)
# 	else:
# 		return JsonResponse({'error': 'Invalid request methon.'}, status=405)


def payment_success(request):
	return render(request, 'payment/payment_success.html', {})