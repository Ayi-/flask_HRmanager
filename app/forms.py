#!/usr/bin/env python
# -*- coding:utf-8 -*-
# ****************************************************************#
# ScriptName: 
# Author: Eli
# Create Date:2015-6-10
# Modify Author:
# Modify Date:
# Function:
# ****************************************************************#
import re

__author__ = 'Eli'
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, EqualTo, Regexp, Email, Optional, NumberRange
from flask import session
from models import User, department, job
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, ValidationError, IntegerField, FloatField, SelectField


class myLogin(Form):
    userName = StringField('name',
                           validators=[DataRequired(u'请输入用户名'), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, u'请输入正确的用户名')])
    Password = PasswordField('Passworld', validators=[DataRequired(message=u'请输入密码')])
    codes = StringField('codes', validators=[DataRequired(u'请输入验证码')])
    remember_me = BooleanField('remember_me', default=False)

    def validate_codes(self, field):
        if session.get('codestrs') != field.data:
            raise ValidationError(u'验证码输入错误！')

    def validate_userName(self, field):
        if not User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名不存在！')


def dep():
    return department.query


class Register(Form):
    userName = StringField('name', validators=[DataRequired(u'请输入用户名')])
    # Regexp验证器来确保用户名字段仅包含字母，数字，下划线以及点符号。
    # 正则表达式Regexp验证器的两个参数一个是正则表达式，一个是验证错误显示的信息
    Password = PasswordField('Passworld', validators=[DataRequired(u'请输入密码'), EqualTo('rPassword', message=u'密码不一致')])
    rPassword = PasswordField('Confirm Passworld', validators=[DataRequired(u'再一次输入密码')])
    email = StringField('email', validators=[DataRequired('请输入正确的邮箱'), Email('邮箱格式错误')])
    workid = IntegerField('workid', validators=[DataRequired(u'请输入您的工号')])
    depart_name = QuerySelectField(query_factory=dep, get_pk=lambda d: d.department_id,
                                   get_label=lambda d: d.department_name)
    manageflag = BooleanField('manageflag', default=False, validators=[Optional()])
    manegepa = PasswordField('manegepa', validators=[Optional()])
    codes = StringField('codes', validators=[DataRequired(u'请输入验证码')])

    def validate_userName(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已存在！')

    def validate_codes(self, field):
        if session.get('codestrs') != field.data:
            raise ValidationError(u'验证码输入错误！')


class alterDep(Form):
    department_name = StringField('department_name', validators=[DataRequired(u'请输入部门名')])
    department_password = StringField('department_password', validators=[DataRequired(u'请输入部门密码!')])  #


class alterWor(Form):
    worker_name = StringField('worker_name', validators=[DataRequired(u'请输姓名!')])  # 员工姓名
    worker_sex = StringField('worker_sex', validators=[DataRequired(u'请输入性别!')])  # 性别
    worker_birthday = StringField('worker_birthday', validators=[DataRequired(u'请输入生日!')])  # 生日
    worker_phone = StringField('worker_phone', validators=[DataRequired(u'请输入联系方式!')])  # 电话
    worker_diploma = StringField('worker_diploma', validators=[DataRequired(u'请输学历!')])  # 学历
    worker_email = StringField('worker_email', validators=[DataRequired(u'请输入邮箱'), Email(u'邮箱格式错误！')])  # 邮箱
    worker_address = StringField('worker_address', validators=[DataRequired(u'请输入家庭地址!')])  # 员工地址
    job_name = StringField('job_name', validators=[DataRequired(u'请输入职务名!')])  # 职务
    department_name = StringField('department_name', validators=[DataRequired(u'请输入部门名!')])  # 部门

    def validate_worker_sex(self, field):
        if field.data not in [u'男', u'女']:
            raise ValidationError(u'性别输入错误！')

    def validate_worker_birthday(self, field):
        if not re.match(r'^(\d{4})-(\d{2})-(\d{2})$', field.data):
            raise ValidationError(u'生日格式错误！')

    def validate_worker_phone(self, field):
        if not re.match(r'^(\d{11})$', field.data):
            raise ValidationError(u'手机格式错误！')

    def validate_job_name(self, field):
        if field.data != u'无':
            j = job.query.filter_by(job_name=field.data).first()
            if not j:
                raise ValidationError(u'职务不存在!')
            else:
                session['jobId'] = j.job_id

    def validate_department_name(self, field):
        if field.data != u'无':
            d = department.query.filter_by(department_name=field.data).first()
            if not d:
                raise ValidationError(u'部门不存在!')
            else:
                session['depId'] = d.department_id


class deleF(Form):
    name = StringField('name', validators=[DataRequired()])


class alterAppraise(Form):
    attendance_count = IntegerField('attendance_count', validators=[Optional(u'请输入出勤次数')])
    achievement = IntegerField('achievement', validators=[Optional(u'请输入本月业绩!')])  #
    appraise_date = StringField('appraise_date', validators=[DataRequired(u'请输入日期或者-符号')])  # 日期

    def validate_attendance_count(self, field):
        if not type(field.data).__name__ == 'int':
            raise ValidationError(u'考勤次数错误')
        if field.data < 0 or field.data > 32:
            raise ValidationError(u'考勤次数错误')

    def validate_achievement(self, field):
        if not type(field.data).__name__ == 'int':
            raise ValidationError(u'业绩输入错误')

    def validate_appraise_date(self, field):
        if field.data!='-':
            if not re.match(r'^(\d{4})-(\d{2})-(\d{2})$', field.data):
                raise ValidationError(u'日期格式错误！')


class alterWages(Form):
    tax = FloatField('tax', validators=[DataRequired(u'请输入税率!'),NumberRange(0,100)])  # 税率
    worker_id = IntegerField('worker_id', validators=[DataRequired(u'请输入员工Id!')])  # 员工
    appraise_id = IntegerField('appraise_id', validators=[DataRequired(u'请输入考勤单号Id!')])  # 员工

    def validate_tax(self, field):
        if not type(field.data).__name__ == 'float':
            raise ValidationError(u'税率格式错误')

class alterJob(Form):
    job_name = StringField('job_name', validators=[DataRequired(u'请输入职务名称!')])   # 职务名称
    job_salary = IntegerField('job_salary', validators=[Optional(u'请输入工资!')])  # 工资
    job_bonus = IntegerField('job_salary', validators=[Optional(u'请输入奖金!')])  # 奖金

class searchF(Form):
    select = SelectField('select')
    data = StringField('data', validators=[DataRequired(u'请输入数据!')])
    startDate = StringField('startDate', validators=[DataRequired(u'请输入日期!')])
    endDate = StringField('endDate', validators=[DataRequired(u'请输入日期!')])  # 生日