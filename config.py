#!/usr/bin/env python
# -*- coding:utf-8 -*-
# ****************************************************************#
# ScriptName: 2015-6-10
# Author: Eli
# Create Date:
# Modify Author:
# Modify Date:
# Function:
# ****************************************************************#

__author__ = 'Eli'

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

dbhost = 'localhost:3306'
dbuser = 'root'
dbpass = '0000'
dbname = 'flask'
# mysql://root:0000@localhost:3306/flask?charset=utf8
SQLALCHEMY_DATABASE_URI = 'mysql://' + dbuser + ':' + dbpass + '@' + dbhost + '/' +dbname+'?charset=utf8'
SQLALCHEMY_COMMIT_ON_TEARDOWN = True

RECAPTCHA_PUBLIC_KEY = '6LcuSggTAAAAANDXUgTpqpWT_c2RO7Mnu4z8n7Jq'
RECAPTCHA_PRIVATE_KEY = '6LcuSggTAAAAANCuIxvrwEWucfCwhiuCRRwOon8g-JgRtu'