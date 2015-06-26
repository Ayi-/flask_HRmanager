#!/usr/bin/env python
# -*- coding:utf-8 -*-
# ****************************************************************#
# ScriptName: views
# Author: Eli
# Create Date:
# Modify Author:
# Modify Date:
# Function:视图模块
# 视图是响应来自网页浏览器的请求的处理器。
# 在Flask中，视图被编写成Python函数，每一个视图函数被映射到一个或多个请求的URL。
# ****************************************************************#


__author__ = 'Eli'

import StringIO, time
from flaskcode import create_validate_code
from flask import render_template, redirect, flash, session, url_for, g, request
from flask.ext.login import login_required, logout_user, current_user, login_user
from models import User, department, workerinfo, delSearchWorker, addWorker, addDepartment, \
    appraise, updateForMysql, addForMysql, wages, job, delToMysql, ROLE_ADMIN, ROLE_USER, ROLE_MANAGER, searchForMysql
from app import app, login_manager, db
from forms import myLogin, Register, alterDep, alterWor, deleF, alterAppraise, alterJob, alterWages, searchF


@app.before_request
def before_request():
    g.user = current_user
    try:
        g.worker = g.user.worker
    except:
        pass


@login_manager.user_loader  # 用于从数据库加载用户
# 这个回调用于从会话中存储的用户 ID 重新加载用户对象
def load_user(userid):
    return User.query.get(userid)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    formL = myLogin(prefix="formL")
    formR = Register(prefix="formR")

    # formR.depart_name.choices=[ (d.department_id,d.department_name) for d in department.query.all()]
    if request.method == 'POST':
        ref = request.form

        if ref['submit'] == 'login':  # 登陆
            if formL.validate_on_submit():
                session['remember_me'] = formL.remember_me.data
                user = User.query.filter_by(username=formL.userName.data).first()
                remember_me = session['remember_me']
                session.pop('remember_me', None)
                login_user(user, remember=remember_me)
                return redirect(url_for("index"))

        if ref['submit'] == 'register':  # 注册
            if formR.validate_on_submit():
                u = User()
                w = workerinfo.query.filter_by(worker_id=int(formR.workid.data)).one()
                u.worker_id = formR.workid.data
                u.username = formR.userName.data
                u.password = formR.Password.data
                w.worker_email = formR.email.data
                db.session.add(u)
                db.session.commit()
                flash('You can now login.')
                return redirect(url_for("login", formR=formR, formL=formL))

            return render_template('login.html', **{'formL': formL, 'formR': formR, 'visibleR': 'visible'})

    return render_template('login.html', **{'formL': formL, 'formR': formR, 'visibleL': 'visible'})


@app.route('/')
@app.route('/index/')  # 路由方法，修饰器方法定义访问地址的时候触发的动作
@login_required
def index():
    return render_template('index.html')


@app.route('/profile', methods=['GET', 'POST'])  # 个人属性页面
@login_required
def profile():
    formWorker = alterWor()

    if request.method == 'POST':
        # 数据copy，不然后续处理会出错
        data = request.form.copy()
        # 选择事件

        sub = data.pop('submit')
        if sub == 'alter':
            if formWorker.validate_on_submit():
                print data
                wid = data.pop('worker_id')
                updateForMysql(data, wid, 'searchworker')
                return redirect(url_for('profile'))
    worker = workerinfo.query.filter_by(worker_id=int(g.user.worker_id)).one()
    return render_template('profile.html', **locals())


# 部门信息查询
@app.route('/searchdepart', methods=['GET', 'POST'])
@app.route('/searchdepart/<int:page>', methods=['GET', 'POST'])
@login_required
def searchdepart(page=1):
    # 创建Form框
    formD = alterDep()
    formDel = deleF()

    if int(g.user.limits) == ROLE_USER:
        dep = department.query.filter_by(delflag=0, department_id=g.worker.department_id).paginate(page, 10, False)

    if int(g.user.limits) == ROLE_ADMIN or int(g.user.limits) == ROLE_MANAGER:
        if request.method == 'POST':
            # 数据copy，不然后续处理会出错
            data = request.form.copy()

            # 选择事件
            sub = data.pop('submit')
            if sub == 'alter':
                # 修改部门
                if formD.validate_on_submit():
                    did = data.pop('id')
                    updateForMysql(data, did, 'searchdepart')
                    return redirect(url_for('searchdepart', page=page))

            if sub == 'delete':
                # 删除部门
                if formDel.validate_on_submit():
                    department.query.filter_by(department_id=data.get('id')).update({'delflag': 1})
                    return redirect(url_for('searchdepart', page=page))

            if sub == 'add':
                if department.query.filter_by(department_name=data.get('department_name')).first():
                    flash(u'部门已存在!')
                    return redirect(url_for('searchdepart', page=page))

                if formD.validate_on_submit():
                    addDepartment(data)
                    return redirect(url_for('searchdepart', page=page))
            altertext = u'部门'
        if int(g.user.limits) == ROLE_MANAGER:
            dep = department.query.filter_by(delflag=0, department_id=g.user.worker.department_id).paginate(page, 10,
                                                                                                            False)
        else:
            dep = department.query.filter_by(delflag=0).paginate(page, 10, False)

    return render_template('searchdepart.html', **locals())


# 员工管理查询使用
@app.route('/searchworker', methods=['GET', 'POST'])
@app.route('/searchworker/<int:page>', methods=['GET', 'POST'])
@login_required
def searchworker(page=1):
    formWorker = alterWor()
    formDelwor = deleF()
    searchForm = searchF()
    searchForm.select.choices = [(3, u'员工ID号'), (4, u'名称(姓名)'), (5, u'日期'), (6, u'性别'), (7, u'职务'), (8, u'部门')]

    if int(g.user.limits) == ROLE_USER:
        wor = workerinfo.query.filter_by(delflag=0, worker_id=g.worker.worker_id).paginate(page, 10, False)

    if int(g.user.limits) == ROLE_ADMIN or int(g.user.limits) == ROLE_MANAGER:
        if request.method == 'POST':
            # 数据处理
            data = request.form.copy()  # 必须copy，否则TypeError: 'ImmutableMultiDict' objects are immutable
            wid = data.get('worker_id')
            if wid:
                data.pop('worker_id')
            sub = data.pop('submit')

            if sub == 'alter':
                if formWorker.validate_on_submit():
                    # 更新数据
                    updateForMysql(data, wid, 'searchworker')
                    return redirect(url_for("searchworker", page=page))

            if sub == 'delete':
                if formDelwor.validate_on_submit():
                    # 删除操作，把标志位设置为0
                    delSearchWorker(wid)
                    return redirect(url_for("searchworker", page=page))

            if sub == 'add':
                if formWorker.validate_on_submit():
                    timeSer = time.strftime("%Y-%m-%d")  # 获取本地时间
                    data['starting_date'] = timeSer
                    page = addWorker(data)
                    return redirect(url_for("searchworker", page=page))
            if sub == 'search':
                wor = searchForMysql(data, 'workerinfo')
                searchFlag = True
                return render_template('searchworker.html', **locals())

                # 读取员工列表
        altertext = u'员工'
        if int(g.user.limits) == ROLE_MANAGER:
            wor = workerinfo.query.filter_by(delflag=0, department_id=g.user.worker.department_id).paginate(page, 10,
                                                                                                            False)
        else:
            wor = workerinfo.query.filter_by(delflag=0).paginate(page, 10, False)
    return render_template('searchworker.html', **locals())


@app.route('/appraisemanage', methods=['GET', 'POST'])  # 考勤管理
@app.route('/appraisemanage/<int:page>', methods=['GET', 'POST'])
@login_required
def appraisemanage(page=1):
    formappraise = alterAppraise()
    searchForm = searchF()
    searchForm.select.choices = [(2, u'考勤ID号'), (4, u'名称(姓名)'), (5, u'日期')]

    if int(g.user.limits) == ROLE_USER:
        Appr = appraise.query.filter_by(worker_id=g.worker.worker_id).paginate(page, 10, False)

    if int(g.user.limits) == ROLE_ADMIN or int(g.user.limits) == ROLE_MANAGER:
        if request.method == 'POST':
            # 数据处理
            data = request.form.copy()  # 必须copy，否则TypeError: 'ImmutableMultiDict' objects are immutable
            appraiseId = data.get('appraise_id')
            if appraiseId:
                data.pop('appraise_id')
            sub = data.pop('submit')
            workerId = data.get('worker_id')

            if sub == 'alter' and formappraise.validate_on_submit():
                updateForMysql(data, appraiseId, 'appraisemanage')
                return redirect(url_for("appraisemanage", page=page))

            if sub == 'add':
                if not workerinfo.query.filter_by(worker_id=workerId).all():
                    flash(u'员工不存在', 'danger')
                    return redirect(url_for("appraisemanage", page=page))

                oneAppraise = appraise.query.order_by(appraise.appraise_date.desc()).filter_by(
                    worker_id=workerId).first()
                if oneAppraise:
                    if oneAppraise.appraise_date.month == time.localtime().tm_mon:
                        flash(u'本员工本月考勤单已经生成，请不要重复创建！', 'danger')
                        return redirect(url_for("appraisemanage", page=page))

                if formappraise.validate_on_submit():
                    # 数据处理
                    addForMysql(data, 'appraise')
                    return redirect(url_for("appraisemanage", page=page))

            if sub == 'search':
                Appr = searchForMysql(data, 'appraise')
                searchFlag = True
                return render_template('appraisemanage.html', **locals())
        altertext = u'考勤'

        if int(g.user.limits) == ROLE_MANAGER:
            Appr = appraise.query.join(workerinfo).filter(appraise.worker_id == workerinfo.worker_id,
                                                          workerinfo.department_id == g.user.worker.department_id).paginate(
                page, 10, False)
        else:
            Appr = appraise.query.paginate(page, 10, False)
    return render_template('appraisemanage.html', **locals())


# 工资管理
@app.route('/wagesmanage', methods=['GET', 'POST'])  # 工资管理
@app.route('/wagesmanage/<int:page>', methods=['GET', 'POST'])
@login_required
def wagesmanage(page=1):
    formWages = alterWages()
    searchForm = searchF()
    searchForm.select.choices = [(1, u'工资ID号'), (2, u'考勤ID号'), (3, u'员工ID号'), (4, u'名称(姓名)'), (5, u'日期')]
    if int(g.user.limits) == ROLE_USER:
        Wage = wages.query.filter_by(worker_id=g.worker.worker_id).paginate(page, 10, False)

    if int(g.user.limits) == ROLE_ADMIN or int(g.user.limits) == ROLE_MANAGER:
        if request.method == 'POST':
            # 数据处理
            data = request.form.copy()  # 必须copy，否则TypeError: 'ImmutableMultiDict' objects are immutable
            print data

            sub = data.pop('submit')

            if sub == 'alter':
                if formWages.validate_on_submit():
                    # 数据处理
                    wagesId = data.get('wages_id')
                    updateForMysql(data, wagesId, 'wagesmanage')
                    return redirect(url_for("wagesmanage", page=page))

            if sub == 'add':
                if not workerinfo.query.filter_by(worker_id=data.get('worker_id')).all():
                    flash(u'员工不存在', 'danger')
                    return redirect(url_for("wagesmanage", page=page))

                workerId = data.get('worker_id')
                appraiseId = data.get('appraise_id')
                if appraise.query.filter_by(worker_id=workerId).filter_by(appraise_id=appraiseId).count() != 1:
                    flash(u'考勤单%s不属于员工%s！' % (appraiseId, workerId), 'danger')
                    return redirect(url_for("wagesmanage", page=page))
                if wages.query.order_by(wages.wage_date.desc()).filter_by(
                        worker_id=workerId).first().wage_date.month == time.localtime().tm_mon:
                    flash(u'本月员工结算工资记录已经创建！', 'danger')
                    return redirect(url_for("wagesmanage", page=page))

                if formWages.validate_on_submit():
                    addForMysql(data, 'wages')
                    return redirect(url_for("wagesmanage", page=page))
            if sub == 'del':
                wagesId = data.get('wages_id')
                delToMysql(wagesId, 'wages')
                return redirect(url_for("wagesmanage", page=page))

            if sub == 'search':
                Wage = searchForMysql(data, 'wages')
                searchFlag = True
                return render_template('wagesmanage.html', **locals())

        if int(g.user.limits) == ROLE_MANAGER:
            Wage = wages.query.join(workerinfo).filter(wages.worker_id == workerinfo.worker_id,
                                                       workerinfo.department_id == g.user.worker.department_id).paginate(
                page, 10, False)
        else:
            Wage = wages.query.filter_by(delflag=0).paginate(page, 10, False)
        altertext = u'工资'
    return render_template('wagesmanage.html', **locals())


# 职务管理
@app.route('/jobmanage', methods=['GET', 'POST'])  # 工资管理
@app.route('/jobmanage/<int:page>', methods=['GET', 'POST'])
@login_required
def jobmanage(page=1):
    fromJob = alterJob()
    if int(g.user.limits) == ROLE_USER:
        Job = job.query.filter_by(job_id=g.worker.job_id).paginate(page, 10, False)

    if int(g.user.limits) == ROLE_ADMIN or int(g.user.limits) == ROLE_MANAGER:
        if request.method == 'POST':
            # 数据处理
            data = request.form.copy()  # 必须copy，否则TypeError: 'ImmutableMultiDict' objects are immutable
            sub = data.pop('submit')

            if sub == 'alter':  # 修改操作
                if fromJob.validate_on_submit():
                    # 数据处理
                    jobId = data.get('jobId')
                    updateForMysql(data, jobId, 'jobmanage')
                    return redirect(url_for("jobmanage", page=page))

            if sub == 'add':  # 添加操作
                if job.query.filter_by(job_name=data.get('job_name')).first():
                    flash(u'职务已经存在')
                    return redirect(url_for("jobmanage", page=page))

                if fromJob.validate_on_submit():
                    addForMysql(data, 'job')
                    return redirect(url_for("jobmanage", page=page))

            if sub == 'del':  # 删除操作
                jobId = data.get('jobId')
                delToMysql(jobId, 'job')
                return redirect(url_for("jobmanage", page=page))
        if int(g.user.limits) == ROLE_MANAGER:
            Job = job.query.filter_by(job_id=g.worker.job_id).paginate(page, 10, False)
        else:
            Job = job.query.filter_by(delflag=0).paginate(page, 10, False)
    return render_template('jobmanage.html', **locals())


# 用户注销
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# 获取验证码
@app.route('/code')
def get_code():  # 验证码显示
    # 把strs发给前端,或者在后台使用session保存
    code_img, strs = create_validate_code()
    buf = StringIO.StringIO()

    code_img.save(buf, 'JPEG', quality=70)
    session['codestrs'] = strs
    buf_str = buf.getvalue()
    response = app.make_response(buf_str)
    return response


@app.errorhandler(404)
def internal_error(error):
    return render_template('error-404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error-500.html'), 500
