#!/usr/bin/env python
# -*- coding:utf-8 -*-
# ****************************************************************#
# ScriptName: __init__
# Author: Eli
# Create Date:2015-6-9
# Modify Author:
# Modify Date:
# Function:初始化脚本
# ****************************************************************#


__author__ = 'Eli'


from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from jinja2 import Environment, PackageLoader

app = Flask(__name__)  # 创建Flask类

app.config.from_object('config')  # 加载默认设置
db = SQLAlchemy(app)  # 初始化数据库链接

env = Environment(loader=PackageLoader('app', 'templates'))

login_manager = LoginManager()  # 设置login
login_manager.init_app(app)
login_manager.login_message = None # 自定义闪现的消息
login_manager.login_view='login'  # 告诉flask这是我们的登陆视图函数
# 当重定向到登入视图，它的请求字符串中会有一个 next 变量，值为用户之前试图 访问的页面。


from app import views,models