
import requests
import re
import sys
# 这两行是为了去除"请求 https 站点取消 ssl 认证时控制台的警告信息"
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

targeturl = sys.argv[1]
version = {'php': '', 'nginx': '', 'apache': '', 'tomcat': ''}


class IsUrlOk():
    def refactorurl(self, url):
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

    def isconnected(self, url):
        global connected
        try:
            requests.get(url, verify=False, timeout=3)
            print("目标站点可达...")
        except IOError:
            print("无法访问站点...")
            sys.exit(0)

    def isurlok(self, url):
        self.refactorurl(url)
        print("正在测试目标站点可访性：", targeturl)
        self.isconnected(targeturl)


class GetResponse:
    global targeturl

    def request(self, dsturl):
        return requests.get(dsturl, verify=False, timeout=3,stream=True)

    def getbynormaltext(self):
        return self.request(targeturl).text

    def getbynormalheaders(self):
        return str(self.request(targeturl).headers)

    def getby404text(self):
        url404 = targeturl + '/asdf'  # asdf.html 有些服务器会响应不同的内容所以不要用
        return self.request(url404).text

    def getby404headers(self):
        url404 = targeturl + '/asdf'
        return str(self.request(url404).headers)

    def getbyphpinfo(self):
        urlphpinfo = targeturl + '/phpinfo.php'
        return self.request(urlphpinfo).text

    def getbyinfo(self):
        urlinfo = targeturl + '/info.php'
        return self.request(urlinfo).text

    def getbyrange(self):
        headers = {'user-agent': 'my-app/0.0.1', 'Range': 'Bytes=1'}
        return requests.get(targeturl, headers=headers, verify=False).text

    def getbyPut(self):
        return requests.put(targeturl, verify=False).text


class GetVersion:

    def returnhome(self):
        return()

    def outputphp(self, statement, xversion):
        print(statement, xversion)
        # sys.exit(0)
        return self.returnhome()

    def refindall(self, keyword, dststr):
        return re.findall(keyword, str(dststr))

    def request(self, dsturl):
        return requests.get(dsturl, verify=False, timeout=3)

    def getphpversion(self):
        version['php'] = self.refindall(
            r"PHP\/\S*", GetResponse.getbynormalheaders(self))
        if version['php']:
            self.outputphp("PHP版本信息（GetByNormal）:", version['php'])
        else:
            version['php'] = self.refindall(
                r"PHP\/\S*", GetResponse.getbynormaltext(self))
            # print(GetResponse.getbynormaltext(self))
            if version['php']:
                self.outputphp("PHP版本信息（GetByNormal）:", version['php'])
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
                        version['php'] = self.refindall("PHP\/\S\S\S\S\S\S*",requests.head(targeturl).headers) #request.get默认只展示302重定向之后的200页面，但是有一种情况 php 信息只存在于302页面的 header 字段
                        if version['php']:
                            self.outputphp("PHP版本信息（GetBy302Page）:", version['php'])

    def getapacheversion(self):
        version['tomcat'] = self.refindall(
            r"Apache\/\S*", GetResponse.getbynormalheaders(self))
        if version['tomcat']:
            self.outputphp("Apache版本信息（GetByNormal）:", version['tomcat'])
        else:
            version['tomcat'] = self.refindall(
                r"Apache\/\S*", GetResponse.getbynormaltext(self))
            if version['tomcat']:
                self.outputphp("Apache版本信息（GetByNormal）:", version['tomcat'])
            else:
                version['tomcat'] = self.refindall(
                    r"Apache\/\S*", GetResponse().getbyphpinfo())
                if version['tomcat']:
                    self.outputphp(
                        "Apache版本信息（GetByphpinfo.php）:", version['tomcat'])
                else:
                    version['tomcat'] = self.refindall(
                        r"Apache\/\S*", GetResponse().getbyinfo())
                    if version['tomcat']:
                        self.outputphp(
                            "Apache版本信息（GetByinfo.php）:", version['tomcat'])

    def getnginxversion(self):
        version['php'] = self.refindall(
            r"nginx\/\S\S\S\S\S*",
            GetResponse.getbynormalheaders(self))
        if version['php']:
            self.outputphp("Nginx版本信息（GetByNormal）:", version['php'])
        else:
            version['php'] = self.refindall(
                r"nginx\/\S\S\S\S\S*",
                GetResponse.getbynormaltext(self))
            if version['php']:
                self.outputphp("Nginx版本信息（GetByNormal）:", version['php'])
            else:
                version['php'] = self.refindall(
                    r"nginx\/\S\S\S\S\S*", GetResponse().getbyphpinfo())
                if version['php']:
                    self.outputphp(
                        "Nginx版本信息（GetByphpinfo.php）:", version['php'])
                else:
                    version['php'] = self.refindall(
                        r"nginx\/\S\S\S\S\S*", GetResponse().getbyinfo())
                    if version['php']:
                        self.outputphp(
                            "Nginx版本信息（GetByinfo.php）:", version['php'])

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

    def getallversion(self):
        self.getphpversion()
        self.gettomcatversion()
        self.getnginxversion()
        self.getapacheversion()

if __name__ == '__main__':
    checkurl = IsUrlOk()
    checkurl.isurlok(targeturl)
    Jewel = GetVersion()
    Jewel.getallversion()
    if version['php']==version['tomcat']==version['tomcat'] == version['php']==[]:
        print("无法探测到任何版本信息，请手工复验")
