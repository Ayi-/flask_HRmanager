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

__author__ = 'Eli'

import sys

reload(sys)
sys.setdefaultencoding('utf8')

import time
from app import db
from flask import flash

ROLE_ADMIN = 0
ROLE_USER = 1
ROLE_MANAGER = 2


class User(db.Model):
    __tablename__ = 'user'

    userid = db.Column('userid', db.Integer, primary_key=True)
    username = db.Column('username', db.String(30), unique=True)
    password = db.Column('password', db.String(20), )
    limits = db.Column('limits', db.VARCHAR(4), default=ROLE_USER)

    worker_id = db.Column(db.Integer, db.ForeignKey('workerinfo.worker_id'), unique=True)
    worker = db.relationship('workerinfo', backref=db.backref('User', cascade="all,delete-orphan", single_parent=True),
                             uselist=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.userid)

    def __repr__(self):
        return '<User %r>' % self.username


class workerinfo(db.Model):  # 员工表
    __tablename__ = 'workerinfo'

    worker_id = db.Column('worker_id', db.Integer, primary_key=True)  # 员工编号
    worker_name = db.Column('worker_name', db.String(10))  # 员工姓名
    worker_sex = db.Column('worker_sex', db.VARCHAR(1))  # 性别
    worker_birthday = db.Column('worker_birthday', db.VARCHAR(10))  # 生日
    worker_phone = db.Column('worker_phone', db.VARCHAR(11))  # 电话
    worker_diploma = db.Column('worker_diploma', db.VARCHAR(10))  # 学历
    worker_email = db.Column('worker_email', db.VARCHAR(50))  # 邮箱
    worker_address = db.Column('worker_address', db.String(100))  # 员工地址
    starting_date = db.Column('starting_date', db.DATE)  # 就职时间
    delflag = db.Column('delflag', db.Boolean, default=0)  # 删除标志位

    job_id = db.Column(db.Integer, db.ForeignKey('job.job_id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.department_id'))

    department = db.relationship('department', backref=db.backref('workerinfo', lazy="dynamic"))
    job = db.relationship('job', backref=db.backref('workerinfo', lazy="dynamic"))

    def __init__(self, data):
        if data.get('worker_id'):
            self.worker_id = data.get('worker_id')
        self.worker_name = data.get('worker_name')
        self.worker_sex = data.get('worker_sex')
        self.worker_birthday = data.get('worker_birthday')
        self.worker_phone = data.get('worker_phone')
        self.worker_diploma = data.get('worker_diploma')
        self.worker_email = data.get('worker_email')
        self.worker_address = data.get('worker_address')
        self.starting_date = data.get('starting_date')
        self.job_id = data.get('job_id')
        self.department_id = data.get('department_id')

    @property
    def get_list(self):
        getList = [self.worker_id, self.worker_name, self.worker_sex, self.worker_birthday,
                   self.worker_phone, self.worker_diploma, self.worker_email, self.worker_address, self.starting_date]
        if self.job:
            getList.append(self.job.job_name)
        else:
            getList.append(u'无')
        if self.department:
            getList.append(self.department.department_name)
        else:
            getList.append(u'无')
        return getList

    def __repr__(self):
        return '<workerinfo %s>' % self.worker_name

    def __unicode__(self):
        return self.worker_name


class job(db.Model):  # 职务表
    __tablename__ = 'job'

    job_id = db.Column('job_id', db.Integer, primary_key=True)  # 职务编号
    job_name = db.Column('job_name', db.String(10), unique=True)  # 职务名称
    job_salary = db.Column('job_salary', db.Integer)  # 职务基本工资
    job_bonus = db.Column('job_bonus', db.Integer)  # 基本奖金

    delflag = db.Column('delflag', db.Boolean, default=0)  # 删除标志位

    def __init__(self,data):
        self.job_name=data.get('job_name')
        self.job_salary=data.get('job_salary')
        self.job_bonus=data.get('job_bonus')

    @property
    def get_list(self):  # 获取数据，添加到列表中
        getList = [self.job_id, self.job_name, self.job_salary,
                   self.job_bonus, self.workerinfo.count()]
        return getList

    def __repr__(self):
        return '<job %s>' % self.job_name

    def __unicode__(self):
        return self.job_name


class department(db.Model):
    __tablename__ = 'department'

    department_id = db.Column('department_id', db.Integer, primary_key=True)  # 部门编号
    department_password = db.Column('department_password', db.VARCHAR(10))  # 经理注册密钥
    department_name = db.Column('department_name', db.String(10), unique=True)  # 部门名
    delflag = db.Column('delflag', db.Boolean, default=0)  # 删除标志位
    # manage_id = db.Column('manage_id',db.Integer, unique=True)  # 经delflag = db.Column('delflag', db.Boolean, default=0)  # 删除标志位理编号


    def __init__(self, data):
        if data.get('department_id'):
            self.department_id = data.get('department_id')
        self.department_name = data.get('department_name')
        self.department_password = data.get('department_password')

    @property
    def get_list(self):
        getList = [self.department_id, self.department_name, self.workerinfo.count(), self.department_password]
        return getList

    def __repr__(self):
        return u'<department %s>' % self.department_name

    def __unicode__(self):
        return self.department_name


class wages(db.Model):  # 工资表
    __tablename__ = 'wages'

    wages_id = db.Column('wages_id', db.Integer, primary_key=True)  # 工资编号
    salary = db.Column('salary', db.Integer)  # 工资
    bonus = db.Column('bonus', db.Float)  # 奖金
    tax = db.Column('tax', db.Float, default=1)  # 税
    real_wages = db.Column('real_wages', db.Float)  # 实际工资
    wage_date = db.Column('wage_date', db.DATE)  # 时间
    delflag = db.Column('delflag', db.Boolean, default=0)  # 删除标志位

    worker_id = db.Column(db.Integer, db.ForeignKey('workerinfo.worker_id'))
    appraise_id = db.Column(db.Integer, db.ForeignKey('appraise.appraise_id'))

    worker = db.relationship('workerinfo',
                             backref=db.backref('wages', lazy='dynamic', cascade="all", single_parent=True,
                                                passive_deletes=True))
    appraise = db.relationship('appraise', backref=db.backref('wages', cascade="all,delete-orphan", single_parent=True),
                               uselist=False)

    def __init__(self, data):
        self.salary = data.get('salary')
        self.bonus = data.get('bonus')
        self.tax = data.get('tax')
        self.real_wages = data.get('real_wages')
        self.wage_date = data.get('wage_date')
        self.worker_id = data.get('worker_id')
        self.appraise_id = data.get('appraise_id')

    @property
    def get_list(self):  # 获取数据，添加到列表中
        getList = [self.wages_id, self.appraise_id, self.worker_id, self.worker.worker_name, self.salary,
                   self.bonus, self.tax, self.real_wages, self.wage_date]
        return getList

    def __repr__(self):
        return '<wages %d>' % self.wages_id


class appraise(db.Model):  # 考核表
    __tablename__ = 'appraise'

    appraise_id = db.Column('appraise_id', db.Integer, primary_key=True)  # 考核编号
    attendance_count = db.Column('attendance_count', db.Integer)  # 考勤次数
    achievement = db.Column('achievement', db.Integer)  # 业绩
    appraise_date = db.Column('appraise_date', db.DATE)  # 时间
    worker_id = db.Column(db.Integer, db.ForeignKey('workerinfo.worker_id'))

    worker = db.relationship('workerinfo',
                             backref=db.backref('appraise', lazy='dynamic', cascade="all", single_parent=True,
                                                passive_deletes=True))

    def __init__(self, data):
        self.achievement = data.get('achievement')
        self.attendance_count = data.get('attendance_count')
        self.worker_id = data.get('worker_id')
        self.appraise_date = data.get('appraise_date')


    @property
    def get_list(self):
        getList = [self.appraise_id, self.worker.worker_name, self.attendance_count, self.achievement,
                   self.appraise_date]
        return getList

    def __repr__(self):
        return '<appraise %d>' % self.appraise_id


def addDepartment(data):
    """
    添加部门信息
    :param data:
    :return:
    """
    try:
        db.session.add(department(data))
        db.session.commit()
    except:
        db.session.rollback()


def addWorker(data):
    """
    添加用户
    :param data:
    :return:
    """
    try:
        jId = job.query.filter_by(job_name=data.get('job_name')).first()
        if jId:
            data['job_id'] = jId.job_id
        else:
            data['job_id'] = None
        dId = department.query.filter_by(department_name=data.get('department_name')).first()
        if dId:
            data['department_id'] = dId.department_id
        else:
            data['department_id'] = None

            db.session.add(workerinfo(data))
            db.session.commit()
            return workerinfo.query.filter_by(delflag=0).paginate(1).total / 10 + 1
    except:
        db.session.rollback()
        flash(u'添加失败', 'danger')


def updateForMysql(data, updateId, targetTable):
    """
    更新数据
    :param data: 更新内容
    :param targetTable:更新对象
    :param updateId: 更新对象ID
    """
    name = ''
    try:
        data.pop('csrf_token')
        if targetTable == 'searchworker':
            name = u'用户'
            jId = job.query.filter_by(job_name=data.get('job_name')).first()
            dId = department.query.filter_by(department_name=data.get('department_name')).first()
            data.pop('job_name')
            data.pop('department_name')
            if jId:
                data['job_id'] = jId.job_id
            else:
                data['job_id'] = None

            if dId:
                data['department_id'] = dId.department_id
            else:
                data['department_id'] = None
            workerinfo.query.filter_by(worker_id=int(updateId)).update(data)

        if targetTable == 'appraisemanage':
            # 只更新attendance_count和achievement
            name = u'考勤'
            data.pop('worker_id')
            appraise.query.filter_by(appraise_id=int(updateId)).update(data)

        if targetTable == 'searchdepart':
            name = u'部门'
            department.query.filter_by(department_id=updateId).update(data)

        if targetTable == 'wagesmanage':
            name = u'工资'
            tax = float(data.get('tax'))

            # 计算结算工资
            oneWages = wages.query.filter_by(wages_id=updateId).one()
            salary = oneWages.salary
            bonus = oneWages.bonus
            real_wages = (salary + bonus) - (salary + bonus) * (tax / 100.0)
            appraise_date = data.get('appraise_date')
            updata = {'tax': tax, 'real_wages': real_wages}
            print updata
            wages.query.filter_by(wages_id=updateId).update(updata)

        if targetTable == 'jobmanage':
            name = u'职务'
            updata={'job_salary':data.get('job_salary'),'job_bonus':data.get('job_bonus'),'job_name':data.get('job_name')}
            job.query.filter_by(job_id=updateId).update(updata)


        db.session.commit()
        flash(u'%s更新成功' % name, 'success')
    except:
        flash(u'%s更新出错' % name, 'danger')
        db.session.rollback()


def addForMysql(data, targetTable):
    """
    添加数据
    :param data:数据
    :param targetTable: 目标表
    :return:
    """
    name = ''
    addModel = None
    try:
        if targetTable == 'appraise':
            print data
            if data.get('appraise_date') == '-':
                data['appraise_date'] = time.strftime("%Y-%m-%d")  # 获取本地时间
            addModel = appraise(data)
            name = '考勤'

        if targetTable == 'wages':
            worker_id = data.get('worker_id')
            appraise_id = data.get('appraise_id')
            oneWorker = workerinfo.query.filter_by(worker_id=worker_id).one()
            oneAppraise = appraise.query.filter_by(appraise_id=appraise_id).one()

            attendance_count = oneAppraise.attendance_count
            achievement = oneAppraise.achievement
            salary = oneWorker.job.job_salary
            bonus = oneWorker.job.job_bonus + attendance_count * 10 + achievement * 20
            tax = float(data.get('tax'))
            real_wages = (salary + bonus) - (salary + bonus) * (tax / 100.0)
            print data
            addData = {'appraise_id': appraise_id, 'worker_id': worker_id, 'salary': salary, 'bonus': bonus, 'tax': tax,
                       'real_wages': real_wages, 'wage_date': time.strftime("%Y-%m-%d")}
            addModel = wages(addData)
            name = '结算工资'

        if targetTable == 'job':
            addModel = job(data)
            name = '职务'

        if addModel:
            db.session.add(addModel)
        db.session.commit()
        flash(u'%s添加成功' % name, 'success')
    except:
        db.session.rollback()
        flash(u'%s添加失败' % name, 'danger')

def delToMysql(delId,targetTable):
    """
    用于删除数据，把删除标志位置为1
    :param delId:目标id
    :param targetTable:目标表
    :return:
    """
    name = ''

    if targetTable == 'job':
        job.query.filter_by(job_id=delId).update({'delflag': 1})
        name = '职务'

    if targetTable == 'wages':
        wages.query.filter_by(wages_id=delId).update({'delflag': 1})
        name = '工资单'

    try:
        db.session.commit()
        flash(u'%s删除成功' % name, 'success')
    except:
        db.session.rollback()
        flash(u'%s删除失败' % name, 'danger')


def delSearchWorker(wid):
    """
    删除用户，只是把标志位置为1
    :param wid:用户ID
    """
    try:
        workerinfo.query.filter_by(worker_id=wid).update({'delflag': 1})
        db.session.commit()
    except:
        db.session.rollback()


def getWorkerForId(wid):
    """
    获取用户
    :param wid:用户ID
    :return: 返回用户对象
    """
    return workerinfo.query.filter_by(worker_id=wid).first()


def searchForMysql(data,targetTable):
    """
    搜索
    :param data:数据
    :param targetTable:目标表
    :return:结果
    """
    select = data.pop('select')
    if targetTable == 'wages':
        if select == '1':  # 工资ID搜索
            return wages.query.filter_by(wages_id=data.get('data')).all()
        if select == '2':  # 考勤ID搜索
            return wages.query.filter_by(appraise_id=data.get('data')).all()
        if select == '3':  # 员工ID搜索
            return wages.query.filter_by(worker_id=data.get('data')).all()
        if select == '4':  # 员工姓名搜索
            return wages.query.join(workerinfo).filter(wages.worker_id==workerinfo.worker_id,workerinfo.worker_name.like('%'+data.get('data')+'%')).all()
        if select == '5':  # 日期搜索
            return wages.query.filter(wages.wage_date >= data.get('startDate')).filter(wages.wage_date<= data.get('endDate')).all()

    if targetTable == 'appraise':
        if select == '2':  # 考勤ID搜索
            return appraise.query.filter_by(appraise_id=data.get('data')).all()
        if select == '4':  # 员工姓名搜索
            return appraise.query.join(workerinfo).filter(appraise.worker_id==workerinfo.worker_id,workerinfo.worker_name.like('%'+data.get('data')+'%')).all()
        if select == '5':  # 日期搜索
            return appraise.query.filter(appraise.appraise_date >= data.get('startDate')).filter(appraise.appraise_date<= data.get('endDate')).all()

    if targetTable == 'workerinfo':
        if select == '3':  # 员工ID搜索
            return workerinfo.query.filter_by(worker_id=data.get('data')).all()
        if select == '4':  # 员工姓名搜索
            return workerinfo.query.filter(workerinfo.worker_name.like('%'+data.get('data')+'%')).all()
        if select == '5':  # 日期搜索
            return workerinfo.query.filter(workerinfo.starting_date >= data.get('startDate')).filter(workerinfo.starting_date<= data.get('endDate')).all()
        if select == '6':  # 性别搜索
            return workerinfo.query.filter_by(worker_sex=data.get('data')).all()
        if select == '7':  # 职务搜索
            return workerinfo.query.join(job).filter(job.job_id==workerinfo.job_id,job.job_name.like('%'+data.get('data')+'%')).all()
        if select == '8':  # 部门搜索
            return workerinfo.query.join(department).filter(department.department_id==workerinfo.department_id,department.department_name.like('%'+data.get('data')+'%')).all()
