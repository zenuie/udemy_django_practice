from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import ObjectDoesNotExist as ObjectDoesNotExist
from carts.models import Cart, Cartitem
from store.models import Product, Variation
from django.contrib.auth.decorators import login_required


# Create your views here.
# Product cookies create
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    # if the user is authenticated
    if current_user.is_authenticated:
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

        is_cart_item_exists = Cartitem.objects.filter(product=product, user=current_user).exists()

        if is_cart_item_exists:
            cart_item = Cartitem.objects.filter(product=product, user=current_user)
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
                item = Cartitem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)
                item.save()
        else:
            cart_item = Cartitem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()
        return redirect('carts')
    # if user not authenticated
    else:
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
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = Cartitem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
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
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = Cartitem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = Cartitem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('carts')


def cart(request, total=0, quantity=0, cart_items=None):
    # 購物車金額、數量計算

    try:
        grand_total, tax = 0, 0
        if request.user.is_authenticated:
            cart_items = Cartitem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = Cartitem.objects.filter(cart=cart, is_active=True).order_by("id")
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


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = Cartitem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = Cartitem.objects.filter(cart=cart, is_active=True).order_by("id")
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
    return render(request, 'store/checkout.html', context)
