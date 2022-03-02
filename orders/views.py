import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from carts.models import Cartitem
from orders.forms import OrderForm
from orders.models import Order, Payment, Orderproduct
import json

from store.models import Product

# 載入驗證
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    # store transctiion tetails inside Payment model
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = Cartitem.objects.filter(user=request.user)

    for item in cart_items:
        print("成功載入")
        print(item.variation)
        order_product = Orderproduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        # variation 同步至 OrderProduct
        cart_item = Cartitem.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        order_product = Orderproduct.objects.get(id=order_product.id)
        order_product.variation.set(product_variation)
        order_product.save()

        # 存貨計算
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # 清除購物車
    Cartitem.objects.filter(user=request.user).delete()

    # 寄送購物清單至email
    mail_subject = '感謝您的購買，以下是購買資訊'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # 以json方式傳送訂單編號以及交易ID
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def place_order(request, total=0, quantity=0):
    current_user = request.user
    total = 0
    quantity = 0
    # 如果購物車為空，則自動導向至商店
    cart_items = Cartitem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':

        form = OrderForm(request.POST)

        if form.is_valid():
            # 商店所有收費資料存在 order
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # 訂單日期格式化
            year = int(datetime.date.today().strftime('%Y'))
            day = int(datetime.date.today().strftime('%d'))
            month = int(datetime.date.today().strftime('%m'))
            Date = datetime.date(year, month, day)
            current_date = Date.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }

            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = Orderproduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transID)

        sub_total = 0
        for total in ordered_products:
            sub_total += total.product_price * total.quantity

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'sub_total': sub_total,
        }
        return render(request, 'orders/order_complete.html', context)

    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
