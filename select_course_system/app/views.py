from django.shortcuts import render_to_response
from index.views import *
from .captcha import *
import  json,logging
import io
# 引入绘图模块
from PIL import Image, ImageDraw, ImageFont
# 引入随机函数模块
import random
from django.contrib import auth

def remoteTrue():#ajax过关
    result = True
    resultDict = {"valid": result}
    resultDict = json.dumps(resultDict)
    return resultDict

def remoteFalse():#ajax不过关
    result = False
    resultDict = {"valid": result}
    resultDict = json.dumps(resultDict)
    return resultDict

#------------------------------------登陆页面---------------------------
def home(request):
    return render(request, "home.html")


#登陆
def checkUser(request):
    if request.method == "POST":
        username = request.POST.get('user')
        password = request.POST.get('password')
        radio = request.POST.get('radio')
        print(username,password,radio)

    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:

        if user.invite[:3] == radio[:3]:
            auth.login(request, user)
            return redirect("/index/home.html")
    return HttpResponse('no')


#接受注册信息
def addCount(request):
    if request.method =="POST":
        no = request.POST.get('no')
        pwd = request.POST.get('password')
        phone = int(request.POST.get('phone'))
        email = request.POST.get('email')
        invite = request.POST.get('invite')
        vc = request.POST.get('vc')

        try:
            if invite[:3] =='tea':
                name = Teacher.objects.get(no = no).name
                user = Count.objects.create_user(username=no, password=pwd, first_name=no, phone=phone, email=email,
                                              invite=invite, name=name)
                user.save()
            elif invite[:3] =='stu':
                name = Student.objects.get(no = no).name
                user = Count.objects.create_user(username=no,password=pwd,first_name=no,phone=phone,email=email,invite=invite,name = name)
            user.save()

            if invite[:3]=='stu':
                try:
                    student_group = Group.objects.get(name='student')
                    user.groups.add(student_group)
                except Exception as e:
                    #出错则删除用户
                    logging.error(e)
                    Count.objects.filter(username = no).delete()
                    print('创建学生用户权限组数据库有错')
                    return HttpResponse("创建用户权限失败!")
            elif invite[:3]=='tea':
                try:
                    teacher_group = Group.objects.get(name='teacher')
                    user.groups.add(teacher_group)
                except Exception as e:
                    logging.error(e)
                    Count.objects.filter(username=no).delete()
                    print('创建老师用户权限组数据库有错')
                    return HttpResponse("创建老师用户权限失败!")
            elif invite[:3]=='adm':
                try:
                    admin_group = Group.objects.get(name='admin')
                    user.groups.add(admin_group)
                except Exception as e:
                    logging.error(e)
                    Count.objects.filter(username=no).delete()
                    print('创建管理员用户权限组数据库有错')
                    return HttpResponse("创建管理员用户权限失败!")
        except Exception as e:
            logging.error(e)
            print('创建用户数据库有错')
            return HttpResponse("创建用户失败!")
    print('no=%s注册成功！'%no)


    return HttpResponse("创建用户成功!")


#检测新用户
def checkNewUser(request):
    if request.method == 'POST':
        no = request.POST.get('username')
        password = request.POST.get('password')
        print('登录名:%s,密码:%s'%(no,password))

        try:
            #count表已存在
            count_obj = Count.objects.get(no=no)
            print('检测新用户:%s' % no + '已存在')
            return HttpResponse(remoteFalse())
        except:
            #不存在
            print('检测新用户:%s' % no + '不存在于Count表')
            #判断数据库中是否由此用户
            try:
                #学生表是否存在
                stu_obj = Student.objects.get(no = no)
                print('检测新用户:%s' % no + '存在于学生表')
            except:
                try:
                    print('检测新用户:%s' % no + '不存在于Student表')
                    #老师表是否存在
                    tea_obj = Teacher.objects.get(no = no)
                    print('检测新用户:%s' % no + '存在于老师表')
                except:
                    try:
                        print('检测新用户:%s' % no + '不存在于Teacher表')
                        adm_obj = Admin.objects.get(no = no)
                        print('检测新用户:%s' % no + '存在于管理者表')
                    except:
                        #学校查无此人
                        return HttpResponse(remoteFalse())

        return HttpResponse(remoteTrue())


#检测忘记密码用户
def checkForgetUser(request):
    if request.method == 'POST':
        no = request.POST.get('no')
        password= request.POST.get('password')
        phone = request.POST.get('phone')
        email =request.POST.get('email')
        invite = request.POST.get('invite')
        vc = request.POST.get('vc')
        print('忘记用户信息:%s,%s,%s,%s,%s,%s'%(no,password,phone,email,invite,vc))

        user = Count.objects.filter(username = no)[0]
        if user:
            if user.email == email:
                if user.phone == phone:
                    if user.invite == invite:
                        user.set_password(password)
                        user.save()
                        return HttpResponse("修改密码成功！")
                    else:
                        return HttpResponse("用户邀请码错误!")
                else:
                    return HttpResponse("用户手机号码错误！")
            else:
                return HttpResponse("用户邮箱错误!")
        else:

            return HttpResponse("未注册！")
#检测邀请码
def checkInvite(request):
    ID = ["stu","tea",'adm']
    if request.method == "POST":
        invite = request.POST.get("invite")
    #规则:前三位必须是字母，如果是
    #tea则是老师,stu则是学生
    #后3-4位为数字,是学生/老师编号
        word = invite[:3].lower()
        num = invite[3:]
        if word not in ID :
            print('错误邀请码:',invite)
        else:
            try:
                #邀请码已存在于count表
                inv_obj = Count.objects.get(invite=invite)
                print('邀请码已被使用:', invite)
            except:
                try:
                    #检测num是否为学生编号
                    stu_obj = Student.objects.get(no = num)
                    print('邀请码%s来自学生表，可使用!'%num)
                    return HttpResponse(remoteTrue())
                except:
                    try:
                        # 检测num是否为老师编号
                        tea_obj = Teacher.objects.get(no = num)
                        print('邀请码%s来自老师表，可使用!' % num)
                        return HttpResponse(remoteTrue())
                    except:
                        try:
                            # 检测num是否为管理者编号
                            adm_obj = Admin.objects.get(no = num)
                            print('邀请码%s来自管理者表，可使用!' % num)
                            return HttpResponse(remoteTrue())
                        except:
                            pass
        return HttpResponse(remoteFalse())

#验证验证码
def verifycodeValid(request):

    if request.method == 'POST':
        vc = request.POST.get('vc')
        print("验证码：",vc)

    if vc.upper() == request.session['verifycode']:
        return HttpResponse(remoteTrue())
    else:
        return HttpResponse(remoteFalse())


#验证码
# def verifycode(request):
#     #定义变量，用于画面的背景色、宽、高
#     bgcolor = (random.randrange(20, 100), random.randrange(20, 100), 255)
#     width = 100
#     height = 25
#     #创建画面对象
#     im = Image.new('RGB', (width, height), bgcolor)
#     #创建画笔对象
#     draw = ImageDraw.Draw(im)
#     #调用画笔的point()函数绘制噪点
#     for i in range(0, 100):
#         xy = (random.randrange(0, width), random.randrange(0, height))
#         fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
#         draw.point(xy, fill=fill)
#     #定义验证码的备选值
#     str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
#     #随机选取4个值作为验证码
#     rand_str = ''
#     for i in range(0, 4):
#         rand_str += str1[random.randrange(0, len(str1))]
#     #构造字体对象
#     font = ImageFont.truetype(font='GOUDYSTO.TTF', size=20)
#     # font = ImageFont.load_default().font
#     #构造字体颜色
#     fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
#     #绘制4个字
#     draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
#     draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
#     draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
#     draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
#     #释放画笔
#     del draw
#     #存入session，用于做进一步验证
#     request.session['verifycode'] = rand_str
#     #内存文件操作
#     buf = io.BytesIO()
#     #将图片保存在内存中，文件类型为png
#     im.save(buf, 'png')
#     #将内存中的图片数据返回给客户端，MIME类型为图片png
#
#     return HttpResponse(buf.getvalue(), 'image/png')


#验证码2
def verifycode(request):
    # 生成图片验证码
    # 调用captcha库中的generate_captcha()函数 返回一个元组 包括：
    # 返回值1 name 验证码名称
    # 返回值2 text 验证码文本
    # 返回值3 value 验证码图片的二进制数据
    name, code, pic = captcha.generate_captcha()
    stream = io.BytesIO(pic)
    image = Image.open(io.BytesIO(pic))
    image.save(stream, "png")
    request.session["verifycode"] = code
    return HttpResponse(stream.getvalue())


def pag_not_found(request):
    """
    全局404配置函数
    """
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):
    """
    全局500配置函数
    """
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response
