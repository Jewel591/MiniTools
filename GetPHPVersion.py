
import requests,re,sys

# 这两行是为了去除"请求 https 站点取消 ssl 认证时控制台的警告信息"
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# with request.urlopen("http://59.67.37.18") as UrlRespone:
#     data = UrlRespone.read()
#     print('Status:', UrlRespone.status, UrlRespone.reason)
#     for k, v in UrlRespone.getheaders():
#         print('%s: %s' % (k, v))
#     print('Data:', data)
# if not sys.argv[0]:
#     print("Please input TargetUrl...")
# targeturl = "http://59.67.37.18"
# print(sys.argv[1])
# if "http" not in sys.argv[1]:
#     targeturl = "http://" + sys.argv[1]
# else:
#     targeturl = sys.argv[1]
connected = 0
tomcatresult = ["Original Response!"]
phpresult = [""]
targeturl = sys.argv[1]


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


def GetPHPVersion(url):
    global targeturl
    global phpresult

    def getbynormal(url):
        global phpresult
        responsenormal = requests.get(url, verify=False, timeout=3)
        phpresult = re.findall("PHP\/\S*", responsenormal.text)
        if not phpresult:
            phpresult = re.findall("PHP\/\S*", str(responsenormal.headers))

        if phpresult:
            print("PHP版本信息（GetByNormal）:", phpresult)
            sys.exit(0)

    def getbyrange(url):
        global tomcatresult
        headers = {'user-agent': 'my-app/0.0.1', 'Range': 'Bytes=1'}
        responserange = requests.get(url, headers=headers, verify=False)
        tomcatresult = re.findall(r"Apache Tomcat\S\S\S\S\S\S\S", responserange.text)
        if tomcatresult:
            print("版本信息（GetByRange）:", tomcatresult)
            sys.exit(0)

    def getbyPut(url):
        global tomcatresult
        responseput = requests.put(url, verify=False)
        # print(responseput.text)
        tomcatresult = re.findall(r"Apache Tomcat\S\S\S\S\S\S\S", responseput.text)
        if tomcatresult:
            print("版本信息（GetByPut）:", tomcatresult)
            sys.exit(0)
    getbynormal(targeturl)
    print("..By404 failed...trying bad Range... ")
    getbyrange(targeturl)
    print("ByRange failed...trying methon PUT...",)
    getbyPut(targeturl)
    print("无法获得版本信息")


RefactorURL(sys.argv[1])
print("正在测试目标站点：", targeturl)
IsConnected(targeturl)
GetPHPVersion(targeturl)
