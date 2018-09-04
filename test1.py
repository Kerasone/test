# -*- coding:utf-8 -*-
import re
import json
import traceback
import numpy as np
#根据类别匹配原文
def getShujv(key,count):
    if len(key)>1:
        if key.find('万')!=-1:
            count=10000*count
        if key.find('千')!=-1:
            count=1000*count
        if key.find('百')!=-1:
            count=100*count
        if key.find('亿')!=-1:
            count=100000000*count
        if key.find('毫')!=-1:
            count=count/1000
        if key.find('毛') != -1:
            count = count / 10
        key,number = re.subn(r'(?:万|千|百|亿|毫|毛)', '', key)
        if key=='':
            key='元'
    if key.find('斤')!=-1 and len(key)<3:
        if key!='公斤':
            count=count*500
        else:
            count=count*1000
        key='克'
    if key=='元钱' or key=='块钱' or key=='人民币' or key=='元人民币' or key=='元整':
        key='元'
    elif key.find('kg')!=-1 or key.find('KG')!=-1 or key.find('公斤')!=-1 or key.find('千克')!=-1:
        key='克'
        count=count*1000
    elif key=='m' or key=='M':
        key='米'
    elif key=='km' or key=='KM' or key=='公里':
        key='米'
        count=count*1000
    elif key=='里':
        key='米'
        count=count*500
    elif key=='cm' or key=='CM'or key=='公分'or key=='厘米':
        key='米'
        count=count/100
    elif key=='mm' or key=='毫米':
        key='米'
        count=count/1000
    elif key == '平方' or key == '平米':
        key = '平方米'
    elif key == '平方厘米':
        key = '平方米'
        count = count / 10000
    elif  key.find('公顷') != -1:
        key = '平方米'
        count = count*10000
    elif key.find('立方') != -1:
        key = '立方米'
    elif key.find('小时') != -1 or key=='h':
        key = '分钟'
        count = count * 60
    elif key.find('秒') != -1 or key == 's':
        key = '分钟'
        count = count /60
    elif key=='MG' or key.find('mg')!=-1:
        key='克'
        count=count/1000
    elif key=='G' or key=='g':
        key='克'
    elif key=='公升':
        key='升'
        count=count*2
    elif key=='ml' or key=='ML' or key=='mL':
        key='升'
        count=count/1000
    elif key=='l' or key=='L':
        key='升'
    elif key=='元港币':
        key='港币'
    return key, count
CN_NUM = {
    '〇' : 0, '一' : 1, '二' : 2, '三' : 3, '四' : 4, '五' : 5, '六' : 6, '七' : 7, '八' : 8, '九' : 9, '零' : 0,
    '壹' : 1, '贰' : 2, '叁' : 3, '肆' : 4, '伍' : 5, '陆' : 6, '柒' : 7, '捌' : 8, '玖' : 9, '貮' : 2, '两' : 2,
}

CN_UNIT = {
    '十' : 10,
    '拾' : 10,
    '百' : 100,
    '佰' : 100,
    '千' : 1000,
    '仟' : 1000,
    '万' : 10000,
    '萬' : 10000,
    '亿' : 100000000,
    '億' : 100000000,
    '兆' : 1000000000000,
}

def chinese_to_arabic(cn:str) -> int:
    unit = 0   # current
    ldig = []  # digest
    for cndig in reversed(cn):
        if cndig in CN_UNIT:
            unit = CN_UNIT.get(cndig)
            if unit == 10000 or unit == 100000000:
                ldig.append(unit)
                unit = 1
        else:
            dig = CN_NUM.get(cndig)
            if unit:
                dig *= unit
                unit = 0
            ldig.append(dig)
    if unit == 10:
        ldig.append(10)
    val, tmp = 0, 0
    for x in reversed(ldig):
        if x == 10000 or x == 100000000:
            val += tmp * x
            tmp = 0
        else:
            tmp += x
    val += tmp
    return val

#获取单位
def getKey(str):
    count = re.search(r'\d+(?:\.\d+)?', str).group()
    if count:
        key = str.replace(count, '')
        key, number = re.subn(r'(?:余|多|几)', '', key)
        return key
#获取数值
def getCount(str):
    count = re.search(r'\d+(?:\.\d+)?', str)
    if count:
        count=count.group()
    return count
def tran2vec(qingjie):
    #读取字典文件
    liangci = open('liangci1.txt').readlines()
    liangci1 = liangci[0]
    liangci1 = json.loads(liangci1)
    #将情节中出现的汉字数字转化为阿拉伯数字
    p = re.compile(r'(\d+(?:\.\d+)?)?[一二三四五六七八九零十百千万亿]+')
    res = p.finditer(qingjie)
    for cn in res:
        cn=cn.group()
        if getCount(cn):
            continue
        else:
            number = chinese_to_arabic(cn)
            qingjie=qingjie.replace(cn,str(number))
    #看情节中是否带有共计、合计
    p0=re.compile(r'\d+(?:\.\d+)?[a-zA-Z\u4e00-\u9fa5]+')
    p1=re.compile(r'(?:共计|合计)(.{0,8})\d+(?:\.\d+)?[a-zA-Z\u4e00-\u9fa5]+')
    m=p1.search(qingjie)#共计价值人民币12159.44元
    key=''
    if m:
        m=m.group()
        m=p0.search(m).group()#12159.44元
        key=getKey(m)
        count=getCount(m)
        key,count=getShujv(key,float(count))
        if key in liangci1:
            liangci1[key]+=count
        m2=p0.findall(qingjie)
        if(m2):
           for key1 in m2:
                if getKey(key1) != key:
                    count1=getCount(key1)
                    key1=getKey(key1)
                    key1,count1=getShujv(key1,float(count1))
                    if key1 in liangci1:
                        liangci1[key1]+=count1
    else:
        m=p0.findall(qingjie)
        if m:
            for key2 in m:
                count2 = getCount(key2)
                key2 = getKey(key2)
                key2,count2=getShujv(key2,float(count2))
                if key2 in liangci1:
                    liangci1[key2]+=count2
    #设置numpy数组不要以科学计数法显示
    np.set_printoptions(suppress=True)
    list2=list(liangci1.values())
        # f1.write(str(i))
        # f1.write('\n')
    array2 = np.array(list2,dtype = float)
    # array3=np.pad(array2, (0, 123), 'constant')
    # print(array2)
    # print(array2.shape)
    return array2
    # f1.close()
tran2vec('昌宁县人民检察院指控，2014年4月19日下午16时许，被告人段某驾拖车经过鸡飞乡澡塘街子，时逢堵车，段某将车停在“冰凉一夏”冷饮店门口，被害人王某的侄子王2某示意段某靠边未果，后上前敲打车门让段某离开，段某遂驾车离开，但对此心生怨愤。同年4月21日22时许，被告人段某酒后与其妻子王1某一起准备回家，走到鸡飞乡澡塘街富达通讯手机店门口时停下，段某进入手机店内对被害人王某进行吼骂，紧接着从手机店出来拿得一个石头又冲进手机店内朝王某头部打去，致王某右额部粉碎性骨折、右眼眶骨骨折。经鉴定，被害人王某此次损伤程度为轻伤一级')

