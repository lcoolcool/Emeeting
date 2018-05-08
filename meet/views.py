# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hashlib
import json
import datetime
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from meet import models
from meet.form import *
from django.db.models import Q
from django.db.utils import IntegrityError


def take_md5(content):
    hash = hashlib.md5()    # 创建hash加密实例
    hash.update(content)    # hash加密
    result = hash.hexdigest()  # 得到加密结果
    return result


def log_out(request):
    del request.session['user_info']
    return redirect('/')


def login(request):
    """
    用户登录
    """
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            password = take_md5(password)
            user = models.UserInfo.objects.filter(name=name, password=password).first()
            if user:
                request.session['user_info'] = {'id': user.id, 'name': user.name}
                return redirect('/')
            else:
                form.add_error('password', '密码错误')
                return render(request, 'login.html', {'form': form})
        else:
            return render(request, 'login.html', {'form': form})


def reg(request):

    if request.method == "GET":
        form = RegForm()
        return render(request, 'reg.html', {'form': form})
    else:
        form = RegForm(request.POST)
        if form.is_valid():  # 获取表单数据
            name = form.cleaned_data['name']
            namefilter = models.UserInfo.objects.filter(name=name)
            if len(namefilter) > 0:
                form.add_error('name', '该用户名已存在!')
            else:
                password = form.cleaned_data['password']
                password2 = form.cleaned_data['password2']

                if password != password2:
                    form.add_error('password2', '两次输入密码不一致!')
                else:
                    emails = form.cleaned_data['emails']
                    password = take_md5(password)
                    userinfo = models.UserInfo(name=name, password=password, emails=emails)
                    userinfo.save()
                    pass
                    return render(request, 'success.html', {'name': name})
        else:
            return render(request, 'reg.html', {'form': form})
    return render(request, 'reg.html', {'form': form})


def fixpassword(request):
    return HttpResponse('想修改密码,留下你的微信!!!!!!!!!!')


def auth_json(func):
    def inner(request, *args, **kwargs):
        user_info = request.session.get('user_info')
        if not user_info:
            return redirect('/login/')
        return func(request, *args, **kwargs)
    return inner


@auth_json
def index(request):
    """
    会议室预定首页
    :param request:
    :return:
    """
    # 拿到所有的时间段
    time_choices = models.Booking.time_choices
    user_info = request.session.get('user_info')
    name = user_info['name']

    return render(request, 'index.html', {'time_choices': time_choices, 'name': name})


@auth_json
def booking(request):
    """
    获取会议室预定情况以及预定会议室
    :param request:
    :param date:
    :return:
    """
    ret = {'code': 1000, 'msg': None, 'data': None}
    current_date = datetime.datetime.now().date()  # 年月日
    if request.method == "GET":
        try:
            fetch_date = request.GET.get('date')  # 拿到前端传过来的转义过的字符串格式的日期
            fetch_date = datetime.datetime.strptime(fetch_date, '%Y-%m-%d').date()  # 转义成时间格式
            if fetch_date < current_date:
                raise Exception('放下过往，着眼当下')
            # 拿到当日的预定信息
            booking_list = models.Booking.objects.filter(booking_date=fetch_date).select_related('user', 'room')\
                .order_by('booking_time')

            booking_dict = {}  # 构建方便查询的大字典
            for item in booking_list:  # item是每一个预定对象
                if item.room_id not in booking_dict:  # 对象的room_id没在字典内
                    booking_dict[item.room_id] = {item.booking_time: {'name': item.user.name, 'id': item.user.id}}
                else:  # 对象的room_id在字典内
                    if item.booking_time not in booking_dict[item.room_id]:  # 但是还有预定信息没在字典内
                        booking_dict[item.room_id][item.booking_time] = {'name': item.user.name, 'id': item.user.id}
            """
            {
                room_id:{
                    time_id:{'user.name':esfsdfdsf,'user.id':1},
                    time_id:{'user.name':esfsdfdsf,'user.id':1},
                    time_id:{'user.name':esfsdfdsf,'user.id':1},
                }
            }
            """

            room_list = models.MeetingRoom.objects.all()  # 数组【所有房间对象】

            booking_info = []
            for room in room_list:
                temp = [{'text': room.title, 'attrs': {'rid': room.id}, 'chosen': False}]
                for choice in models.Booking.time_choices:
                    v = {'text': '', 'attrs': {'time-id': choice[0], 'room-id': room.id}, 'chosen': False}
                    if room.id in booking_dict and choice[0] in booking_dict[room.id]:  # 说明已有预定信息
                        v['text'] = booking_dict[room.id][choice[0]]['name']  # 预订人名
                        v['chosen'] = True
                        if booking_dict[room.id][choice[0]]['id'] != request.session['user_info']['id']:
                            v['attrs']['disable'] = 'true'
                            v['attrs']['class'] = 'unable'  # 不可对别人预定的房间进行操作
                    temp.append(v)
                booking_info.append(temp)
            ret['data'] = booking_info
        except Exception as e:
            ret['code'] = 1001
            ret['msg'] = str(e)
        return JsonResponse(ret)
    else:
        try:
            # 拿到预定的日期并进行转义
            booking_date = request.POST.get('date')
            booking_date = datetime.datetime.strptime(booking_date, '%Y-%m-%d').date()
            if booking_date < current_date:
                raise Exception('放下过往，着眼当下')

            # SELECTED_ROOM = {del: {roomId:timeId}, add: {roomId:timeId}};
            booking_info = json.loads(request.POST.get('data'))
            for room_id, time_id_list in booking_info['add'].items():
                if room_id not in booking_info['del']:
                    continue
                for time_id in list(time_id_list):
                    # 同时点了增加和删除，即用户在选择之后反悔了。。
                    if time_id in booking_info['del'][room_id]:
                        booking_info['del'][room_id].remove(time_id)
                        booking_info['add'][room_id].remove(time_id)

            add_booking_list = []
            for room_id, time_id_list in booking_info['add'].items():
                for time_id in time_id_list:
                    obj = models.Booking(
                        user_id=request.session['user_info']['id'],
                        room_id=room_id,
                        booking_time=time_id,
                        booking_date=booking_date
                    )
                    add_booking_list.append(obj)
            models.Booking.objects.bulk_create(add_booking_list)  # 批量添加，增加数据库效率

            remove_booking = Q()
            for room_id, time_id_list in booking_info['del'].items():
                for time_id in time_id_list:
                    temp = Q()
                    temp.connector = 'AND'
                    temp.children.append(('user_id', request.session['user_info']['id'],))
                    temp.children.append(('booking_date', booking_date,))
                    temp.children.append(('room_id', room_id,))
                    temp.children.append(('booking_time', time_id,))
                    remove_booking.add(temp, 'OR')
            if remove_booking:
                models.Booking.objects.filter(remove_booking).delete()
        except IntegrityError as e:
            ret['code'] = 1011
            ret['msg'] = '会议室已被预定'

        except Exception as e:
            ret['code'] = 1012
            ret['msg'] = '预定失败：%s' % str(e)

    return JsonResponse(ret)
