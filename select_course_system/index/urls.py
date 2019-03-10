#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'home.html',views.home),
    url(r'admin_index$',views.admin_index),#管理员界面
    url(r'admin_index_info$',views.admin_index_info),#管理员获取信息接口
    url(r'teacher_index$',views.teacher_index),#老师界面
    url(r'student_index$',views.student_index),#学生界面
    url(r'handle.html',views.handle),#处理页角色甄别
    url(r'student_handle$',views.student_handle),#学生处理页
    url(r'teacher_handle$', views.teacher_handle),#老师处理页
    url(r'admin_handle$', views.admin_handle),#管理员处理页
    url(r'admin_handle_modal$', views.admin_handle_modal),#管理员处理页模态框接口
    url(r'admin_handle_info$',views.admin_handle_info),#管理员获取信息接口
    url(r'update_stu_cou$',views.update_stu_cou),#更新学生成绩表
    url(r'setting.html',views.setting),#设置页
    url(r'profile.html',views.profile),#个人页
    url(r'set_avatar$',views.set_avatar),#修改头像
    url(r'set_advertisement$', views.set_advertisement),  # 修改广告
    url(r'set_profile$',views.set_profile),#修改个人信息
    url(r'set_password$',views.set_password),#修改密码
    url(r'logout',views.logout),#登出

]