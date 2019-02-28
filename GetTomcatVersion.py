
import requests
import re
import sys

# 这两行是为了去除"请求 https 站点取消 ssl 认证时控制台的警告信息"
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

tomcatresult = ["Original Response!"]
try:
    targeturl = sys.argv[1]
except IndexError:
    print("请输入目标站点(可以不用加协议)...")
    sys.exit(0)

def RefactorURL(url):
    global targeturl
    if not targeturl:
        print("请输入目标站点...")
        sys.exit(0)
    else:
        if re.findall("http", url):
            return
        else:
            if re.findall(":443", url):
                targeturl = "https://" + sys.argv[1]
                return
            else:
                targeturl = "http://" + sys.argv[1]
                return


def IsConnected(url):
    global connected
    try:
        requests.get(url, verify=False, timeout=3)
    except IOError:
        print("无法访问站点...")
        sys.exit(0)


def GetTomcatVersion(url):
    global targeturl
    global tomcatresult

    def getby404(url):
        global tomcatresult
        url404 = url + '/asdf'  # asdf.html 有些服务器会响应不同的内容所以不要用
        response404 = requests.get(url404, verify=False, timeout=3)
        tomcatresult = re.findall(
            "Apache Tomcat\S\S\S\S\S\S\S",
            response404.text)
        # print(response404.headers)
        if tomcatresult:
            print("Tomcat版本信息（GetBy404）:", tomcatresult)
            sys.exit(0)
        else:
            tomcatresult = re.findall("Apache Tomcat\S\S\S\S\S\S\S", str(response404.headers))
            if tomcatresult:
                print("Tomcat版本信息（GetBy404）:", tomcatresult)

    def getbyrange(url):
        global tomcatresult
        headers = {'user-agent': 'my-app/0.0.1', 'Range': 'Bytes=1'}
        responserange = requests.get(url, headers=headers, verify=False)
        tomcatresult = re.findall(
            r"Apache Tomcat\S\S\S\S\S\S\S",
            responserange.text)
        if tomcatresult:
            print("Tomcat版本信息（GetByRange）:", tomcatresult)
            sys.exit(0)

    def getbyPut(url):
        global tomcatresult
        responseput = requests.put(url, verify=False)
        # print(responseput.text)
        tomcatresult = re.findall(
            r"Apache Tomcat\S\S\S\S\S\S\S",
            responseput.text)
        if tomcatresult:
            print("Tomcat版本信息（GetByPut）:", tomcatresult)
            sys.exit(0)

    getby404(targeturl)
    print("..By404 failed...trying bad Range... ")
    getbyrange(targeturl)
    print("ByRange failed...trying methon PUT...", )
    getbyPut(targeturl)
    print("无法获得版本信息")


RefactorURL(sys.argv[1])
print("正在测试目标站点：", targeturl)
IsConnected(targeturl)
GetTomcatVersion(targeturl)
