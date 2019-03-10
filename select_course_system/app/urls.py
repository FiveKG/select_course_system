"""select_course_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views

urlpatterns = [
    #url(r'$', views.home),
    url(r'home', views.home),
    url(r'checkUser$',views.checkUser),#检测用户
    url(r'checkNewUser$', views.checkNewUser),#检验新用户
    url(r'checkForgetUser$',views.checkForgetUser),#检验忘记密码用户信息
    url(r'addCount', views.addCount),
    url(r'verifycodeValid$', views.verifycodeValid),  # 验证验证码
    url(r'verifycode', views.verifycode),#验证码
    url(r'checkInvite',views.checkInvite),#验证邀请码





]
