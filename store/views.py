from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from carts.models import Cartitem
from carts.views import _cart_id
from .models import Product
from category.models import Category


# Create your views here.
# 商品頁面
def store(request, category_slug=None):
    # 商品分類
    categories = None

    # 商品項目
    products = None

    # 如果商品存在
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')

    # 商品數量
    product_count = products.count()
    # 商品一頁顯示幾個
    pagination = Paginator(products, 2)
    # 商品分頁
    page = request.GET.get('page')
    paged_products = pagination.get_page(page)
    context = {
        'products': paged_products,
        'product_count': product_count,
    }

    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = Cartitem.objects.filter(cart__cart_id=_cart_id(request), product=single_product)
    except Exception as e:
        raise e
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product-detail.html', context)
