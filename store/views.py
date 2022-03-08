from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from carts.models import Cartitem
from carts.views import _cart_id
from .forms import ReviewForm
from .models import Product, Reviewrating
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
    print(category_slug,product_slug)
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = Cartitem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product-detail.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        try:
            reviews = Reviewrating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            print(url)
            messages.success(request, "感謝您的評論")
            return redirect(url)
        except Reviewrating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = Reviewrating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                print(url)
                # messages.success(request, '您好，您的評論已經送出')
                return redirect(url)
