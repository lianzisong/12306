import urllib.request as ur
import urllib.error as uerror
import urllib.parse as up
import time
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup as bs
import ssl
import json
import string




date = "2017-01-03"
from_station = "XMS" #厦门
to_station = "LYS" #龙岩
purpose_codes = "ADULT"

mailto_list=['xxxx@163.com']
mail_host="smtp.163.com"  #设置服务器
mail_user="xxxx"    #用户名
mail_pass=""   #口令
mail_postfix="163.com"  #发件箱的后缀

SWITCH = False
before =""
after = ""

INDEX = 'https://kyfw.12306.cn/otn/leftTicket/queryA'


def QueryTrain():
    context = ssl._create_unverified_context()
    url = INDEX + "?"+"leftTicketDTO.train_date="+date+"&leftTicketDTO.from_station="\
        +from_station+"&leftTicketDTO.to_station="+to_station+"&purpose_codes="+purpose_codes
    req = ur.Request(url,method='GET')
    #req = ur.Request(INDEX)
    try:
        response = ur.urlopen(req,context=context)
        jdata_str = response.read().decode('utf-8')
        ret = ParseJson(jdata_str)
        if len(ret) != 0:
            content = Format(ret)
            title = date +"   " +from_station +"---"+to_station
            SendMailNotify(content,title)
    except uerror.HTTPError as e:
        print(e.reason)
    except uerror.URLError as e:
        print(e.reason)
    except Exception as e:
        print(e)
    finally:
        return

def ParseJson(jdata_str):
    jdata = json.loads(jdata_str,encoding='utf-8')
    ret = list()
    print(type(jdata))
    if 'data' in jdata:
        datas = jdata["data"]
        for data in datas:
            if 'queryLeftNewDTO' in data:
                queryLeftNewDTO = data['queryLeftNewDTO']
                start_time = queryLeftNewDTO["start_time"]
                arrive_time = queryLeftNewDTO["arrive_time"]
                zy_num = queryLeftNewDTO["zy_num"]
                ze_num = queryLeftNewDTO["ze_num"]
                if CheckCon(start_time,arrive_time,zy_num,ze_num):
                    train = dict()
                    train["start_time"] = start_time
                    train["arrive_time"] = arrive_time
                    train["zy_num"] = zy_num
                    train["ze_num"] = ze_num
                    ret.append(train)
    return ret



def CheckCon(start_time,arrive_time,zy_num,ze_num):
    if SWITCH:
        pass
    if ze_num != "无" and ze_num !="--": #second class
        return True

    if zy_num != "无" and zy_num != "--": #first class
        return True

    return False

def Format(unformat):
    content = str()
    content = "\t\t\t\n"
    content += "\t\t出发\t\t\t到达\t\t\t一等\t\t\t二等\n"
    for item in unformat:
        content += "\t\t"+item["start_time"]+"\t\t\t"+item["arrive_time"]+"\t\t\t"+item["zy_num"]+"\t\t\t"+item["ze_num"]+"\n"
    return content



def SendMailNotify(content,title):
    me = "hello" + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = title
    msg['From'] = me
    msg['To'] = ";".join(mailto_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(me, mailto_list, msg.as_string())
        server.close()
    except Exception as e:
        print(str(e))

if __name__ == "__main__" :
    QueryTrain()