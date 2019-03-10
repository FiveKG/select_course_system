from django.shortcuts import render,redirect,reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission,Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import  F,Q
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from app.models import *
import json,logging
#判断身份
def if_radio(request):
    radio = request.user.invite[:3]
    if radio =='stu':
        radio = '学生'
        return radio
    elif radio == 'tea':
        radio = '老师'
        return radio
    elif radio == 'adm':
        radio = '管理员'
        return radio

#首页
@login_required
def home(request):
    print('???')
    radio = if_radio(request)

    if radio == "学生":
        return redirect('/index/student_index')
    elif radio =="老师":
        return redirect('/index/teacher_index')
    elif radio =="管理员":
        return redirect('/index/admin_index')

#操作
@login_required
def handle(request):
    radio = if_radio(request)

    if radio == "学生":
        return redirect('/index/student_handle')
    elif radio == "老师":
        return redirect('/index/teacher_handle')
    elif radio == "管理员":
        return redirect('/index/admin_handle')

@login_required
def teacher_handle(request):
    # 获取老师信息
    radio = if_radio(request)
    email = request.user.email
    avatar = request.user.avatar
    teacher_obj = Teacher.objects.get(no=str(request.user))
    name = teacher_obj.name
    no = teacher_obj.no

    #tbody
    all_course_obj = Courses.objects.filter(teacher_id=str(request.user))
    content = {}

    for course in all_course_obj:
        course_name = course.name
        all_stu_cou_obj = Stu_cou.objects.filter(cou_id=course_name)  # 所有选择了老师这门课程的学生成绩表
        # 每个选了这门课程的学生信息
        stu_content_list = []
        for stu_cou_obj in all_stu_cou_obj:
            stu_content_dict = {}
            student_obj = Student.objects.filter(no=str(stu_cou_obj.stu_id))[0]

            stu_content_dict['student_id'] = stu_cou_obj.stu_id
            stu_content_dict['performance'] = stu_cou_obj.performance
            stu_content_dict['student_name'] = student_obj.name
            stu_content_dict['student_cclass'] = student_obj.cclass_id

            stu_content_list.append(stu_content_dict)

        content[course_name] = stu_content_list

    if request.method =='GET':
        return render(request,'teacher_handle.html',locals())

@login_required
def admin_handle(request):
    # 获取管理者信息
    radio = if_radio(request)
    email = request.user.email
    avatar = request.user.avatar
    admin_obj = Admin.objects.get(no=str(request.user))
    name = admin_obj.name
    no = admin_obj.no

    if request.method =='GET':
        return render(request,'admin_handle.html',locals())

@login_required
def student_handle(request):
    # 获取学生信息
    radio = if_radio(request)
    email = request.user.email
    avatar = request.user.avatar
    student_obj = Student.objects.get(no=str(request.user))
    name = student_obj.name
    no = student_obj.no
    age = student_obj.age

    #显示已选学科
    stu_cou_obj = Stu_cou.objects.filter(stu_id=str(request.user)).values('cou_id')
    selected_course = []
    for course in stu_cou_obj:
        selected_course.append(course.get('cou_id'))

    # 获取课程信息
    all_course_obj = Courses.objects.all()
    content={}
    for course_obj in all_course_obj:
        temp_dict= {}
        course_time = course_obj.time
        course_credit = course_obj.credit
        teacher_name = Teacher.objects.filter(no=course_obj.teacher_id)[0].name
        temp_dict["course_time"] = course_time
        temp_dict["course_credit"] = course_credit
        temp_dict["teacher_name"] = teacher_name

        content[course_obj.name] = temp_dict

    if request.method == "GET":
        return render(request,"student_handle.html",locals())
    if request.method=='POST':
        selected_course_str = json.dumps(selected_course)
        return HttpResponse(selected_course_str)

@login_required
def update_stu_cou(request):
    #学生选课
    if if_radio(request) =='学生':
        stu_cou_obj = Stu_cou.objects.filter(stu_id =str(request.user))
        if len(stu_cou_obj) >=3:
            return HttpResponse("只能选择3门课程")

        if request.method == "POST":
            course = request.POST.get('course')
            course_time = request.POST.get('course_time')
            course_credit = request.POST.get('course_credit')
            teacher_name = request.POST.get('teacher_name')
            Stu_cou.objects.create(cou_id = course,stu_id = request.user.username)
            print(request.user,'选择新课程：',course,'学分为:',course_credit,'学时为:',course_time,'任课老师为:',teacher_name)
            return HttpResponse("yes")
        return HttpResponse('更新失败')

    #老师改成绩
    if if_radio(request)=="老师":
        if request.method =='POST':
            student_id = request.POST.get("student_id")
            performance = request.POST.get("performance")
            course = request.POST.get("course")
            stu_cou_obj = Stu_cou.objects.get(Q(stu_id=student_id) & Q(cou_id=course))
            print(student_id,'更改课程:',course,'分数从：',stu_cou_obj.performance,'改为:',performance)
            stu_cou_obj.performance=performance
            stu_cou_obj.save()
            return HttpResponse("yes")
        return HttpResponse('更新失败')



@login_required
def student_index(request):
    #获取学生信息
    radio = if_radio(request)
    email = request.user.email
    avatar = request.user.avatar
    student_obj = Student.objects.get(no=str(request.user))
    name = student_obj.name
    no = student_obj.no
    age =student_obj.age

    #获取教室信息
    cclass = student_obj.cclass_id
    cclass_obj = Class.objects.get(name=cclass)
    amount = cclass_obj.num
    special = cclass_obj.special_id

    #获取课程信息
    stu_cou_obj = Stu_cou.objects.filter(stu = str(request.user))
    content={}
    for item in stu_cou_obj:
        temp_dict={}

        course_obj = Courses.objects.get(name = item.cou_id)
        course_time = course_obj.time
        course_credit = course_obj.credit
        teacher_id = Stu_cou.objects.filter(cou= item.cou).values("cou__teacher")[0].get('cou__teacher')
        teacher_name = Teacher.objects.filter(no = teacher_id)[0].name

        temp_dict["course_time"] = course_time
        temp_dict["course_credit"]=course_credit
        temp_dict["teacher_name"]=teacher_name
        temp_dict["performance"] = item.performance

        content[item.cou_id]=temp_dict

    if request.method == 'GET':
        return render(request,'student_index.html',locals())

@login_required
def teacher_index(request):
    # 获取老师信息
    radio = if_radio(request)
    email = request.user.email
    avatar = request.user.avatar
    teacher_obj = Teacher.objects.get(no=str(request.user))
    name = teacher_obj.name
    no = teacher_obj.no
    age = teacher_obj.age
    institute = teacher_obj.institute_id#所在院系
    all_course_obj = Courses.objects.filter(teacher_id = str(request.user))

    course_num = all_course_obj.count()#课程数量
    student_num = 0#学生数量
    content={}

    for course in all_course_obj:
        course_name = course.name
        all_stu_cou_obj = Stu_cou.objects.filter(cou_id = course_name)#所有选择了老师这门课程的学生成绩表
        student_num += all_stu_cou_obj.count()#这门课程的学生数量
        # 每个选了这门课程的学生信息
        stu_content_list = []
        for stu_cou_obj in all_stu_cou_obj:
            stu_content_dict = {}

            student_obj = Student.objects.filter(no = str(stu_cou_obj.stu_id))[0]

            stu_content_dict['student_id'] = stu_cou_obj.stu_id
            stu_content_dict['performance'] = stu_cou_obj.performance
            stu_content_dict['student_name'] = student_obj.name
            stu_content_dict['student_cclass'] = student_obj.cclass_id

            stu_content_list.append(stu_content_dict)

        content[course_name]=stu_content_list


    if request.method =='GET':
        return render(request,'teacher_index.html',locals())

@login_required
def admin_index(request):
    # 获取管理者信息
    radio = if_radio(request)
    email = request.user.email
    avatar = request.user.avatar
    admin_obj = Admin.objects.get(no=str(request.user))
    name = admin_obj.name
    no = admin_obj.no

    #head信息
    head_no = no
    head_institute = Institute.objects.all().count()
    head_special = Special.objects.all().count()
    head_course = Courses.objects.all().count()
    head_class = Class.objects.all().count()
    head_register = Count.objects.all().count()
    head_teacher = Teacher.objects.all().count()
    head_student = Student.objects.all().count()

    #tbody,institute_info
    institute_info =[]
    all_institute_obj = Institute.objects.all()
    for institute_obj in all_institute_obj:
        temp_dict={}
        temp_dict[institute_obj.name]=institute_obj.spe_num

        institute_info.append(temp_dict)

    if request.method =='GET':
        return render(request,'admin_index.html',locals())





#检测对象是否已经注册
def if_register(request,obj,dict):
    if Count.objects.filter(username = obj.no):
        dict["register"] = 'yes'
        return dict
    else:
        dict["register"] = 'no'
        return dict

@login_required
def select_option(request,radio):
    #给select插件提供数据list
    select_option = []
    if radio == 'teacher':
        #老师按照学院划分,返回所有院系名称
        all_institute_obj = Institute.objects.all()
        for institute_obj in all_institute_obj:
            select_option.append(institute_obj.name)
    if radio =='student':
        #学生按照班级划分,返回所有班级名称
        all_class_obj = Class.objects.all()
        for class_obj in all_class_obj:
            select_option.append(class_obj.name)
    if radio == 'course':
        #课程按老师划分,返回所有老师名称
        all_teacher_obj = Teacher.objects.all()
        for teacher_obj in all_teacher_obj:
            select_option.append(teacher_obj.name)
    if radio == 'special':
        #专业按照院系划分,返回所有院系名称
        all_institute_obj = Institute.objects.all()
        for institute_obj in all_institute_obj:
            select_option.append(institute_obj.name)
    if radio == 'cclass':
        #班级按照专业划分,返回所有专业名称
        all_special_obj = Special.objects.all()
        for special_obj in all_special_obj:
            select_option.append(special_obj.name)

    return select_option

@login_required
def tbody_interface(request,post_body):
    #给tbody提供tr,格式{xxx:{a:a,b:b....}}
    tbody = {}
    radio = post_body.get('radio')
    current_select_value = post_body.get('current_select_value')
    if radio =='teacher':
        all_teacher_obj = Teacher.objects.filter(institute_id = current_select_value)

        for teacher_obj in all_teacher_obj:
            temp_dict = {}
            temp_dict["name"]= teacher_obj.name
            temp_dict["age"] = teacher_obj.age
            temp_dict["from"] = teacher_obj.institute_id
            #是否注册
            temp_dict = if_register(request, teacher_obj, temp_dict)
            tbody[teacher_obj.no] = temp_dict

    elif radio =='student':
        all_student_obj = Student.objects.filter(cclass_id=current_select_value)

        for student_obj in all_student_obj:
            temp_dict={}
            temp_dict["name"] = student_obj.name
            temp_dict["age"] = student_obj.age
            temp_dict["from"] = student_obj.cclass_id
            # 是否注册
            temp_dict = if_register(request, student_obj, temp_dict)
            tbody[student_obj.no] = temp_dict

    elif radio =='register':
        register_type = post_body.get('current_select_value')
        if register_type == "registered_student":
            all_count_obj = Count.objects.all()
            for count_obj in all_count_obj:
                temp_dict = {}
                if count_obj.invite[:3] == 'stu':
                    student_obj = Student.objects.get(no=count_obj.username)
                    temp_dict['name'] = count_obj.name
                    temp_dict['age'] = student_obj.age
                    temp_dict['from'] = student_obj.cclass_id
                    # 是否注册
                    temp_dict = if_register(request, student_obj, temp_dict)
                    tbody[count_obj.username] = temp_dict

        if register_type == "registered_teacher":
            all_count_obj = Count.objects.all()
            for count_obj in all_count_obj:
                temp_dict = {}
                if count_obj.invite[:3] == 'tea':
                    teacher_obj = Teacher.objects.get(no=count_obj.username)
                    temp_dict['name'] = count_obj.name
                    temp_dict['age'] = teacher_obj.age
                    temp_dict['from'] = teacher_obj.institute_id
                    # 是否注册
                    temp_dict = if_register(request, teacher_obj, temp_dict)
                    tbody[count_obj.username] = temp_dict

        if register_type == "unregister_student":
            all_student_obj = Student.objects.all()
            for student_obj in all_student_obj:
                temp_dict = {}
                try:
                    count_obj = Count.objects.get(username=student_obj.no)
                except Exception as e:
                    temp_dict['name'] = student_obj.name
                    temp_dict['age'] = student_obj.age
                    temp_dict['from'] = student_obj.cclass_id
                    # 是否注册
                    temp_dict = if_register(request, student_obj, temp_dict)
                    tbody[student_obj.no] = temp_dict

        if register_type == "unregister_teacher":
            all_teacher_obj = Teacher.objects.all()
            for teacher_obj in all_teacher_obj:
                temp_dict = {}
                try:
                    count_obj = Count.objects.get(username=teacher_obj.no)
                except Exception as e:
                    temp_dict['name'] = teacher_obj.name
                    temp_dict['age'] = teacher_obj.age
                    temp_dict['from'] = teacher_obj.institute_id
                    # 是否注册
                    temp_dict = if_register(request, teacher_obj, temp_dict)
                    tbody[teacher_obj.no] = temp_dict
    elif radio == 'course':
        teacher_obj = Teacher.objects.get(name=current_select_value)
        all_course_obj = Courses.objects.filter(teacher_id = teacher_obj.no)

        for course_obj in all_course_obj:
            temp_dict = {}
            temp_dict["time"] = course_obj.time
            temp_dict["credit"] =course_obj.credit
            tbody[course_obj.name] = temp_dict
    elif radio == 'special':
        all_sepcial_obj = Special.objects.filter(ins_id = current_select_value)
        for special_obj in all_sepcial_obj:
            temp_dict = {}
            temp_dict['num'] = special_obj.num
            tbody[special_obj.name] = temp_dict
    elif radio == 'cclass':
        all_class_obj = Class.objects.filter(special_id = current_select_value)
        for class_obj in all_class_obj:
            temp_dict = {}
            temp_dict['num'] =class_obj.num
            tbody[class_obj.name] = temp_dict
    return tbody

@login_required
def modal_interface(request,post_body):
    #给模态框提供数据list,[a,b,c]
    modal = []
    from_data = post_body.get('from')
    data = post_body.get('data')
    if from_data == 'institute':
        #返回该院系的专业信息
        all_special_obj = Special.objects.filter(ins_id = data)
        for special_obj in all_special_obj:
            modal.append(special_obj.name)
    elif from_data == 'special':
        # 返回选择该专业的班级信息
        all_class_obj = Class.objects.filter(special_id = data)
        for class_obj in all_class_obj:
            modal.append(class_obj.name)
    elif from_data == 'cclass':
        #返回该班级的所有学生姓名
        all_student_obj =Student.objects.filter(cclass_id = data)
        for student_obj in all_student_obj:
            modal.append(student_obj.name)
    return modal

@login_required
def admin_index_info(request):
    #interface == select_option 提供下拉菜单数据,发送方数据格式：{"interface":"select_option","radio":"teacher"}
    #interface == tbody 提供tbody数据,发送方数据格式：{"interface":"tbody","radio":id,"current_select_value":current_select_value}
    #interface == modal 提供modal数据,发送方数据格式：data:{"interface":"modal","data":institute,"from":"institute"}
    if request.method == 'POST':
        interface = request.POST.get('interface')
        post_body = request.POST
        print('进入admin_index_info接口,当前请求接口为：',interface,'请求体为：',post_body)
        if interface =='select_option':
            select = select_option(request,request.POST.get("radio"))
            arg = json.dumps(select)
            if select:
                print('select_option接口返回数据成功!')
            else:
                print('select_option接口返回数据为空!')
            return HttpResponse(arg)
        elif interface=='tbody':
            tbody = tbody_interface(request,request.POST)
            arg = json.dumps(tbody)
            if tbody:
                print('tbody接口返回数据成功')
            else:
                print('tbody接口返回数据为空!')
            return HttpResponse(arg)
        elif interface=='modal':
            modal = modal_interface(request,request.POST)
            arg = json.dumps(modal)
            if modal:
                print('modal接口返回数据成功')
            else:
                print('modal接口返回数据为空!')
            return HttpResponse(arg)

    return HttpResponse('no')

@login_required
def admin_handle_delete(request,post_body):
    #管理员删除接口
    where = post_body.get('where')
    no = post_body.get('no')
    result = False
    #查看客户表是否有此用户，有则删除
    count_obj = Count.objects.filter(username=no)
    if count_obj:
        count_obj.delete()

    if where == 'teacher':
        teacher_obj = Teacher.objects.get(no = no).delete()
        result = True
        return result
    elif where =='student':
        student_obj = Student.objects.get(no = no).delete()
        result = True
        return result
    elif where =='cclass':
        cclass = post_body.get('name')
        cclass_obj = Class.objects.get(name = cclass).delete()
        result = True
        return result
    elif where == 'special':
        special = post_body.get('name')
        special_obj = Special.objects.get(name=special).delete()
        result = True
        return result
    return result

@login_required
def admin_handle_add(request,post_body):

    # 管理员添加接口
    where = post_body.get('where')
    no = post_body.get('no')
    name = post_body.get('name')
    age = post_body.get('age')
    result = False

    if where == 'teacher':
        print('no=',no)
        if Teacher.objects.filter(no =no):
            print('{}老师已存在'.format(name))
            return result
        institute = post_body.get('institute')
        Teacher.objects.create(no =no,age=age,name=name,institute_id=institute)
        result = True
        return result
    elif where =='student':
        if Student.objects.filter(no=no):
            print('{}学生已存在'.format(name))
            return result
        cclass = post_body.get('cclass')
        Student.objects.create(no =no,age=age,name=name,cclass_id=cclass)
        Class.objects.filter(name= cclass).update(num= F('num')+1)
        result = True
        return result
    elif where =='cclass':
        if Class.objects.filter(name = name):
            print('{}班级已存在'.format(name))
            return result
        special = post_body.get('special')
        cclass = post_body.get('cclass')
        Class.objects.create(name=cclass,special_id =special)
        Special.objects.filter(name = special).update(num= F('num')+1)
        result = True
        return result
    elif where == 'special':
        if Special.objects.filter(name = name):
            print('{}专业已存在'.format(name))
            return result
        institute = post_body.get('institute')
        Special.objects.create(name= name,ins_id = institute)
        result = True
        return result
    return result

@login_required
def admin_handle_update(request,post_body):
    # 管理员更新接口
    result = False
    where = post_body.get('where')
    if where =='courses':
        time = post_body.get('time')
        credit = post_body.get('credit')
        Courses.objects.filter(name = post_body.get('name')).update(time=time,credit=credit)
        result = True
        return result
    return result

@login_required
def admin_handle_info(request):
    #delete:data ={'handle':delete,'where':teacher/student/cclass'no':no};
    #add:data ={'handle':'add','where':teacher/student/cclass'no':no,'name':name,'age':age,'institute':in...};
    print('admin_handle_info接口进入')
    no = request.POST.get("no")
    if request.method == 'POST':
        handle = request.POST.get("handle")
        post_body = request.POST
        print(post_body)
        if handle == 'delete':
            result = admin_handle_delete(request,post_body)
            print('admin_handle_info接口删除no:{}，操作结果{}'.format(no,str(result)))
            if result:
                return HttpResponse('yes')
        elif handle =='add':
            result = admin_handle_add(request,post_body)
            print('admin_handle_info接口添加no:{}，操作结果{}'.format(no, str(result)))
            if result:
                return HttpResponse('yes')
        elif handle =='update':
            result = admin_handle_update(request,post_body)
            print('admin_handle_update接口添加no:{}，操作结果{}'.format(no, str(result)))
            if result:
                return HttpResponse('yes')

    return HttpResponse('no')


def remoteTrue():#ajax规则过关
    result = True
    resultDict = {"valid": result}
    resultDict = json.dumps(resultDict)
    return resultDict

def remoteFalse():#ajax规则不过关
    result = False
    resultDict = {"valid": result}
    resultDict = json.dumps(resultDict)
    return resultDict


@login_required
def admin_handle_modal(request):
    if request.method=='POST':
        data = request.POST
        for key,value in data.items():
            if key =='special_name':
                special_obj = Special.objects.filter(name=value)
                if special_obj:
                    #已存在
                    return HttpResponse(remoteFalse())
                else:
                    return HttpResponse(remoteTrue())
            if key =="teacher_no":
                teacher_obj = Teacher.objects.filter(no = value)
                if teacher_obj:
                    #已存在
                    return HttpResponse(remoteFalse())
                else:
                    return HttpResponse(remoteTrue())
            elif key =='student_no':
                student_obj = Student.objects.filter(no = value)
                if student_obj:
                    #已存在
                    return HttpResponse(remoteFalse())
                else:
                    return HttpResponse(remoteTrue())
            elif key =='cclass_name':
                class_obj = Class.objects.filter(name = value)
                if class_obj:
                    #已存在
                    return HttpResponse(remoteFalse())
                else:
                    return HttpResponse(remoteTrue())

    return HttpResponse(remoteTrue())



#登出
@login_required
def logout(request):
    auth.logout(request)
    return redirect("/app/home")

#设置界面
@login_required
def setting(request):
    email = request.user.email
    radio = if_radio(request)
    avatar = request.user.avatar

    name=None
    if if_radio(request)=='学生':
        name = Student.objects.get(no=str(request.user)).name
    if if_radio(request)=='老师':
        name = Teacher.objects.get(no=str(request.user)).name
    if if_radio(request)=='管理员':
        name = Admin.objects.get(no=str(request.user)).name
    if request.method == 'GET':
        return render(request,'setting.html',locals())

#个人信息
@login_required
def profile(request):
    email = request.user.email
    radio = if_radio(request)
    date_joined = request.user.date_joined.strftime('%Y-%m-%d')
    phone = request.user.phone
    invite = request.user.invite
    avatar = request.user.avatar
    if if_radio(request) == '学生':
        name = Student.objects.get(no =str(request.user)).name
    elif if_radio(request) == '老师':
        name = Teacher.objects.get(no =str(request.user)).name
    elif if_radio(request) == "管理员":
        name = Admin.objects.get(no =str(request.user)).name

    if request.method == 'GET':
        return render(request, 'profile.html', locals())

#修改头像
@login_required
def set_avatar(request):
    if request.method =='POST':
        #修改头像
        img_files = request.FILES.get('avatar')
        if not img_files:
            return redirect('app/setting.html')

        filedir = 'static/img/avatar/'
        filepath = filedir + str(request.user) + '_avatar.png'
        file = open(filepath, 'wb+')
        for line in img_files.chunks():
            file.write(line)
        file.close()

        #更新头像
        count = Count.objects.filter(username=request.user)
        if count:
            count.update(avatar = filepath)
        else:
            return HttpResponse('请重新登陆！')
    return redirect('/index/setting.html')

#修改广告
@login_required
def set_advertisement(request):
    if request.method =='POST':
        #修改头像
        img_files = request.FILES.get('advertisement')
        if not img_files:
            return HttpResponse('文件为空')

        filedir = 'static/img/advertisement/'
        filepath = filedir + str(request.user) + '_advertisement.png'
        file = open(filepath, 'wb+')
        for line in img_files.chunks():
            file.write(line)
        file.close()

    return redirect('/index/admin_handle.html')


#修改个人信息
@login_required()
def set_profile(request):
    if request.method =="POST":
        tagName = request.POST.get("tagName")
        tagData = request.POST.get("tagData")

        print("更新数据{}:{}".format(tagName, tagData))
        count = Count.objects.filter(username = request.user)
        if tagName in ['email','phone']:
            if tagName == "email":
                count.update(email=tagData)
                return HttpResponse("yes")
            elif tagName == "phone":
                count.update(phone=tagData)
                return HttpResponse("yes")
    return HttpResponse("更新失败!")

#修改密码
@login_required()
def set_password(request):
    if request.method =='POST':

        oldPassword = request.POST.get("oldPassword")
        newPassword = request.POST.get("newPassword")
        print('oldPassword:', oldPassword)
        print('newPassword:', newPassword)
        if not request.user.check_password(oldPassword):
            print('密码更新错误：原密码错误')
            return HttpResponse('password wrong')
        else:
            request.user.set_password(newPassword)
            request.user.save()
            print('密码更新成功')
            auth.logout(request)
            return HttpResponse('yes')

    return HttpResponse('no')