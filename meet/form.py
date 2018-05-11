# coding:utf-8
from django.forms import Form
from django.forms import fields
from django.forms import widgets
from captcha.fields import CaptchaField


class LoginForm(Form):
    name = fields.CharField(
        required=True,
        error_messages={'required': '用户名不能为空'},
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名', 'id': 'name'})
    )
    password = fields.CharField(
        required=True,
        error_messages={'required': '密码不能为空'},
        widget=widgets.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码', 'id': 'password'})
    )


class RegForm(Form):
    name = fields.CharField(
        required=True,
        error_messages={'required': '用户名不能为空'},
        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名', 'id': 'name'})
    )
    password = fields.CharField(
        required=True,
        error_messages={'required': '密码不能为空'},
        widget=widgets.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码', 'id': 'password'})
    )
    password2 = fields.CharField(
        required=True,
        error_messages={'required': '请再次输入密码'},
        widget=widgets.PasswordInput(attrs={'class': 'form-control', 'placeholder': '确认密码', 'id': 'password2'})
    )
    emails = fields.EmailField(
        required=True,
        error_messages={'required': '请输入邮箱'},
        widget=widgets.EmailInput(attrs={'class': 'form-control', 'placeholder': '邮箱', 'id': 'emails'})
    )
#    captcha = CaptchaField(
#       required=True,
#        error_messages={'required': '请输入邮箱'},
#        widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名', 'id': 'name'})
#    )

