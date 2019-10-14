import requests
import re
import sys
import threading
import time
import subprocess
# 这两行是为了去除"请求 https 站点取消 ssl 认证时控制台的警告信息"
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

version = {'php': '', 'nginx': '', 'apache': '', 'tomcat': ''}
# keyword = {
#     'php':'PHP Version\s\S\S\S\S\S\S\S',
#     'tomcat':'Apache Tomcat\S\S\S\S\S\S\S',
#     'nginx':'nginx\/\S\S\S\S\S*',
#     'apache':'Apache\/\S*'}

targeturl = ""


class IsUrlOk():
    def refactorurl(self, url):
        global targeturl
        if re.findall("http", url):
            return
        else:
            if re.findall(":\d?443", url):
                targeturl = "https://" + sys.argv[1]
                print("检测到x443端口,默认尝试 https")
                return
            else:
                targeturl = "http://" + sys.argv[1]
                return

    def isconnected(self, url):
        global connected
        try:
            requests.get(url, verify=False, timeout=3)
            print("目标站点可达...")
        except IOError:
            print("无法访问站点...")
            sys.exit(0)

    def isurlok(self, url):
        global targeturl
        try:
            targeturl = sys.argv[1]
        except IndexError:
            print("请输入目标站点...")
            sys.exit(0)
        self.refactorurl(targeturl)
        print("正在测试目标站点可访性：", targeturl)
        self.isconnected(targeturl)


class GetResponse:
    global targeturl

    def request(self, dsturl):
        try:
            return requests.get(dsturl, verify=False, timeout=5)
        except :
            # print("连接超时，默认timeout:5 url:", dsturl)
            return ""

    def getbynormaltext(self):
        return self.request(targeturl).text

    def getbynormalheaders(self):
        return str(self.request(targeturl).headers)

    def getby404text(self):
        url404 = targeturl + '/as.df'  # asdf.html 有些服务器会响应不同的内容所以不要用
        return self.request(url404).text

    def getby404headers(self):
        url404 = targeturl + '/as.df'
        return str(self.request(url404).headers)

    def getbyphpinfo(self):
        urlphpinfo = targeturl + '/phpinfo.php'
        try:
            return self.request(urlphpinfo).text
        except:
            return self.request(urlphpinfo)

    def getbyinfo(self):
        urlinfo = targeturl + '/info.php'
        try:
            resultinfo = str(self.request(urlinfo).headers) + str(self.request(urlinfo).text)
            return resultinfo

        except:
            return self.request(urlinfo)

    def getbyrange(self):
        headers = {'user-agent': 'my-app/0.0.1', 'Range': 'Bytes=1'}
        return requests.get(
            targeturl,
            headers=headers,
            verify=False,
            timeout=5).text

    def getbyPut(self):
        try:
            return requests.put(targeturl, verify=False, timeout=5).text
        except IOError:
            # print("目标站点不支持 PUT 方法...")
            return


class GetVersion:

    def outputphp(self, statement, xversion):
        print(statement, xversion)

    def refindall(self, keyword, dststr):
        try:
            return (re.findall(keyword, str(dststr)))[0]
        except IndexError:
            return re.findall(keyword, str(dststr))

    def request(self, dsturl):
        try:
            return requests.get(dsturl, verify=False, timeout=5)
        except IOError:
            # print("连接超时，默认timeout:5 url:",dsturl)
            return ""

    def getphpversion(self):
        version['php'] = self.refindall(
            r"PHP\/\S*", GetResponse.getbynormalheaders(self))
        if version['php']:
            self.outputphp("PHP版本信息（GetByNormal）:", version['php'])
        else:
            version['php'] = self.refindall(
                r"PHP\/\S*", GetResponse.getbynormaltext(self))
            if version['php']:
                self.outputphp("PHP版本信息（GetByNormal）:", version['php'])
            else:
                version['php'] = self.refindall(
                    r"PHP\/\S*", GetResponse.getby404headers(self))
                if version['php']:
                    self.outputphp("PHP版本信息（GetBy404Page）:", version['php'])
                else:
                    version['php'] = self.refindall(
                        r"PHP Version\s\S\S\S\S\S\S\S",
                        GetResponse().getbyphpinfo())
                    if version['php']:
                        self.outputphp(
                            "PHP版本信息（GetByphpinfo.php）:", version['php'])
                    else:
                        version['php'] = self.refindall(
                            r"PHP Version\s\S\S\S\S\S\S\S", GetResponse().getbyinfo())
                        if version['php']:
                            self.outputphp(
                                "PHP版本信息（GetByinfo.php）:", version['php'])
                        else:
                            version['php'] = self.refindall(
                                r"PHP\/\S*", GetResponse().getbyinfo())
                            if version['php']:
                                self.outputphp(
                                    "PHP版本信息（GetByinfo.php/404）:", version['php'])
                                # request.get默认只展示302重定向之后的200页面，但是有一种情况 php
                                # 信息只存在于302页面的 header 字段
                            else:
                                try:
                                    version['php'] = self.refindall(
                                        r"PHP\/\S\S\S\S\S\S*", requests.head(targeturl).headers)
                                except:
                                    version['php'] =""
                                if version['php']:
                                    self.outputphp(
                                        "PHP版本信息（GetBy302Page）:", version['php'])

    def getapacheversion(self):
        version['apache'] = self.refindall(
            r"Apache\/\S*", GetResponse.getbynormalheaders(self))
        if version['apache']:
            self.outputphp("Apache版本信息（GetByNormal）:", version['apache'])
        else:
            version['apache'] = self.refindall(
                r"Apache\/\S*", GetResponse.getbynormaltext(self))
            if version['apache']:
                self.outputphp("Apache版本信息（GetByNormal）:", version['apache'])
            else:
                version['apache'] = self.refindall(
                    r"Apache\/\S*", GetResponse().getbyphpinfo())
                if version['apache']:
                    self.outputphp(
                        "Apache版本信息（GetByphpinfo.php）:", version['apache'])
                else:
                    version['apache'] = self.refindall(
                        r"Apache\/\S*", GetResponse().getbyinfo())
                    if version['apache']:
                        self.outputphp(
                            "Apache版本信息（GetByinfo.php）:", version['apache'])

    def getnginxversion(self):
        version['nginx'] = self.refindall(
            r"nginx\/\S\S\S\S\S*",
            GetResponse.getbynormalheaders(self))
        if version['nginx']:
            self.outputphp("Nginx版本信息（GetByNormal）:", version['nginx'])
        else:
            version['nginx'] = self.refindall(
                r"nginx\/\S\S\S\S\S*",
                GetResponse.getbynormaltext(self))
            if version['nginx']:
                self.outputphp("Nginx版本信息（GetByNormal）:", version['nginx'])
            else:
                version['nginx'] = self.refindall(
                    r"nginx\/\S\S\S\S\S*", GetResponse().getbyphpinfo())
                if version['nginx']:
                    self.outputphp(
                        "Nginx版本信息（GetByphpinfo.php）:", version['nginx'])
                else:
                    version['nginx'] = self.refindall(
                        r"nginx\/\S\S\S\S\S*", GetResponse().getbyinfo())
                    if version['nginx']:
                        self.outputphp(
                            "Nginx版本信息（GetByinfo.php）:", version['nginx'])

    def gettomcatversion(self):
        version['tomcat'] = self.refindall(
            r"Apache Tomcat\S\S\S\S\S\S\S",
            GetResponse.getby404headers(self))
        if version['tomcat']:
            self.outputphp("Tomcat版本信息（GetBy404）:", version['tomcat'])
        else:
            version['tomcat'] = self.refindall(
                r"Apache Tomcat\S\S\S\S\S\S\S",
                GetResponse.getby404text(self))
            if version['tomcat']:
                self.outputphp("Tomcat版本信息（GetBy404）:", version['tomcat'])
            else:
                version['tomcat'] = self.refindall(
                    r"Apache Tomcat\S\S\S\S\S\S\S",
                    GetResponse().getbyrange())  # 因为getbyrange（）中没有使用 self.xxx，所以不需要传递 self
                if version['tomcat']:
                    self.outputphp(
                        "Tomcat版本信息（GetByBadRange）:",
                        version['tomcat'])
                else:
                    version['tomcat'] = self.refindall(
                        r"Apache Tomcat\S\S\S\S\S\S\S", GetResponse().getbyPut())
                    if version['tomcat']:
                        self.outputphp(
                            "Tomcat版本信息（GetByMethonPut）:", version['tomcat'])
#                    else:
#                        payload = "curl "+targeturl+" -X PROPFIND -i"
#                        version['tomcat'] = self.refindall(
#                            r"Apache Tomcat\S\S\S\S\S\S\S", subprocess.getoutput(payload))
#                        if version['tomcat']:
#                            self.outputphp(
#                                "Tomcat版本信息（GetByBadMethon）:", version['tomcat'])

    def getallversion(self):
        self.getphpversion()
        self.gettomcatversion()
        self.getnginxversion()
        self.getapacheversion()


if __name__ == '__main__':
    timestart = time.time()
    checkurl = IsUrlOk()
    checkurl.isurlok(targeturl)
    timemiddle = time.time()
    Jewel = GetVersion()
    # Jewel.getallversion()
    for i in (
            Jewel.getphpversion(),
            Jewel.gettomcatversion(),
            Jewel.getnginxversion(),
            Jewel.getapacheversion()):
        t = threading.Thread(target=i)
        t.start()
    timeend = time.time()
    if len(
        version['php']) == len(
        version['apache']) == len(
            version['tomcat']) == len(
                version['nginx']) == 0:
        print("无法探测到任何版本信息")
        print("请手动尝试命令：curl -ki -X PROPFIND "+targeturl)
    print("scanned in " + str(timeend - timestart) + " seconds")
    # print("检索耗时：", timeend - timemiddle)
