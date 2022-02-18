import current as current
import retro as retro
from django.http import HttpResponse

from accounts.forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
# 載入驗證
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name,
                                               username=username, email=email,
                                               password=password)
            user.phone_number = phone_number
            user.save()

            # 使用者驗證(email)
            current_site = get_current_site(request)
            mail_subject = '請開通你的帳號'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request, '註冊成功')
            return redirect('/accounts/login/?command=verification&email=' + email)
    else:
        form = RegistrationForm
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, '恭喜登入')
            return redirect('dashboard')
        else:
            messages.error(request, '請輸入正確的帳號密碼')
            return redirect('login')
    return render(request, 'accounts/signin.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, '恭喜登出～')
    return redirect('login')


# 帳號申請驗證部分
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, '恭喜驗證成功')
        return redirect('login')

    else:
        messages.success(request, '驗證碼失效')
        return redirect('register')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # 重設密碼
            current_site = get_current_site(request)
            mail_subject = '重設您的密碼'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, '密碼重設連結已寄送到您的信箱了')
            return redirect('login')
        else:
            messages.error(request, '此信箱不存在！')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


# 密碼重設驗證
def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, '請重設您的密碼')
        return redirect('resetPassword')
    else:
        messages.success(request, '連結已失效')
        return redirect('login')
    return HttpResponse('ok')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, '重設密碼成功')
            return redirect('login')
        else:
            messages.error(request, '請確認密碼是否相同')
            return redirect('resetPassword')
    return render(request, 'accounts/resetPassword.html')
