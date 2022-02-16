from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import ObjectDoesNotExist as ObjectDoesNotExist
from carts.models import Cart, Cartitem
from store.models import Product, Variation


# Create your views here.
# Product cookies create
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                  variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass
    product = Product.objects.get(id=product_id)
    try:
        # get the cart using the cart_id present in the session
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()

    is_cart_item_exists = Cartitem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exists:
        cart_item = Cartitem.objects.filter(product=product, cart=cart)
        # existing_variations -> database
        # current_variation -> product_variation
        # item_id -> database
        ex_var_list = []  # 現有的款式
        id = []
        for item in cart_item:
            existing_variation = item.variation.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        # 合併類型相同購物車內容
        if product_variation in ex_var_list:
            # increase the item quantity
            index = ex_var_list.index(product_variation)
            item_id = id[index]
            item = Cartitem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = Cartitem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                item.variation.clear()
                item.variation.add(*product_variation)
            item.save()
    else:
        cart_item = Cartitem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        if len(product_variation) > 0:
            cart_item.variation.clear()
            for item in product_variation:
                cart_item.variation.add(item)
        cart_item.save()
    return redirect('carts')


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = Cartitem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('carts')


def delete_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = Cartitem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('carts')


def cart(request, total=0, quantity=0, cart_items=None):
    # 購物車金額、數量計算
    grand_total, tax = 0, 0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = Cartitem.objects.filter(cart=cart, is_active=True).order_by('id')
        print(cart_items)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)
