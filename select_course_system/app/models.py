from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Class(models.Model):
    name = models.CharField(primary_key=True,max_length=10)
    num = models.IntegerField(default=0  )
    special = models.ForeignKey("Special")

class Special(models.Model):
    name = models.CharField(primary_key=True, max_length=10)
    num = models.IntegerField(default=0)
    # courses = models.ManyToManyField("Courses")
    ins = models.ForeignKey("Institute")

class Courses(models.Model):
    name = models.CharField(primary_key=True, max_length=10)
    time = models.IntegerField()
    credit = models.IntegerField()
    teacher = models.ForeignKey("Teacher")

class Teacher(models.Model):
    no = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=10,default=0)
    age = models.IntegerField()
    institute = models.ForeignKey("Institute")

class Institute(models.Model):
    name = models.CharField(primary_key=True, max_length=10)
    spe_num = models.IntegerField(default=0)


class Student(models.Model):
    no = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=10)
    age = models.IntegerField()
    cclass = models.ForeignKey("Class")


class Stu_cou(models.Model):
    performance = models.IntegerField(null=True)
    stu = models.ForeignKey("Student")
    cou = models.ForeignKey("Courses")

#管理员
class Admin(models.Model):
    no = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=10)

# 存储账号信息
class Count(AbstractUser):
    phone = models.CharField(max_length=13)
    name = models.CharField(max_length=20)
    invite = models.CharField(max_length=9)
    avatar= models.CharField(max_length=40)


    #adm：admin  tea: 老师 stu：学生



