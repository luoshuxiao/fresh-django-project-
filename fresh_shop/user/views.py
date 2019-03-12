from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from fresh_shop.settings import ORDER_NUMBER, READ_RECENTLY
from goods.models import Goods
from order.models import OrderInfo
from user.forms import RegisterForm, LoginForm, AddressForm
from user.models import User, UserAddress


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            #  账号不存在于数据库，密码和确认密码一致，邮箱格式正确
            username = form.cleaned_data['user_name']
            password = make_password(form.cleaned_data['pwd'])
            email = form.cleaned_data['email']
            User.objects.create(username=username, password=password, email=email)
            return HttpResponseRedirect(reverse('user:login'))
        else:
            # 获取表单验证不通过的错误信息
            errors = form.errors
            return render(request, 'register.html', {'errors': errors})


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user = User.objects.filter(username=username)[0]
            request.session['user_id'] = user.id
            return HttpResponseRedirect(reverse('goods:index'))
        else:
            errors = form.errors
            return render(request, 'login.html', {'errors': errors})


def logout(request):
    if request.method == 'GET':
        #  删除session中的id值
        # del request.session['user_id']
        #  清空当前登陆session记录
        request.session.flush()
        #  如果只是删除user_id的话，在退出时需要判断session中是否有商品信息，
        #       没有商品信息就不删除session中的商品信息
        # if request.session.get('goods'):
        #     del request.session['goods']
        return HttpResponseRedirect(reverse('goods:index'))


def user_center_info(request):
    if request.method == 'GET':
        id = request.session['user_id']
        user = User.objects.filter(id=id)[0]
        address = user.useraddress_set.all()[0]
        #  返回一个标识符 （用户中心下的分类标签的样式设置，
        #  方便前端base_user.html实现在那个页面下就让那个页面的分类标签变颜色）
        active = 'info'
        #  返回最近浏览商品列表
        r_list = request.session.get('read_list')
        if r_list != [] and r_list != None:
            #   如果最近浏览大于五个商品只取五个商品，没有大于就取全部
            read_list = r_list[:READ_RECENTLY:] if len(r_list) > READ_RECENTLY else r_list
            #   通过id取商品对象
            recently_read_goods = [Goods.objects.filter(id=goods_id).first() for goods_id in read_list]
        else:
            recently_read_goods = []
        return render(request, 'user_center_info.html', {'address': address,
                                                         'active': active, 'recently_read_goods': recently_read_goods})


def user_center_order(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        page = int(request.GET.get('page', 1))
        #  查询当前用户产生的所有订单信息
        order = OrderInfo.objects.filter(user_id=user_id)
        status = OrderInfo.ORDER_STATUS
        pg = Paginator(order, ORDER_NUMBER)
        orders = pg.page(page)
        #  返回一个标识符 （用户中心下的分类标签的样式设置，
        #  方便前端base_user.html实现在那个页面下就让那个页面的分类标签变颜色）
        active = 'order'
        return render(request, 'user_center_order.html', {'orders': orders, 'status': status, 'active': active})


def user_center_site(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        user_address = UserAddress.objects.filter(user_id=user_id)
        #  返回一个标识符 （用户中心下的分类标签的样式设置，
        #  方便前端base_user.html实现在那个页面下就让那个页面的分类标签变颜色）
        active = 'site'
        return render(request, 'user_center_site.html', {'user_address': user_address, 'active': active})
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            address = form.cleaned_data['address']
            postcode = form.cleaned_data['postcode']
            mobile = form.cleaned_data['mobile']
            user_id = request.session.get('user_id')
            UserAddress.objects.create(user_id=user_id,
                                       address=address,
                                       signer_name=username,
                                       signer_mobile=mobile,
                                       signer_postcode=postcode)
            return HttpResponseRedirect(reverse('user:user_center_site'))

        else:
            errors = form.errors
            return render(request, 'user_center_site.html', {'errors': errors})
