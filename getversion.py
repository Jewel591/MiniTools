
# import GetApacheVersion
# import GetPHPVersion
import requests
import re
import sys
# 这两行是为了去除"请求 https 站点取消 ssl 认证时控制台的警告信息"
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

tomcatversion = [""]
nginxversion = [""]
apacheversion = [""]
phpversion = [""]
targeturl = sys.argv[1]


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
        except IOError:
            print("无法访问站点...")
            sys.exit(0)

    def isurlok(self, url):
        self.refactorurl(url)
        print("正在测试目标站点可访性：", targeturl)
        self.isconnected(targeturl)


class GetResponse:
    global targeturl

    def request(self,dsturl):
        return requests.get(dsturl, verify=False, timeout=3)

    def getbynormaltext(self):
        return self.request(targeturl)

    def getbynormalheaders(self):
        return self.request(targeturl).headers

    def getby404text(self):
        url404 = targeturl + '/asdf'  # asdf.html 有些服务器会响应不同的内容所以不要用
        return self.request(url404).text

    def getby404headers(self):
        url404 = targeturl + '/asdf'
        return self.request(url404).headers

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

    def outputphp(self,statement,xversion):
        print(statement, xversion)
        # sys.exit(0)
        return self.returnhome()

    def refindall(self, keyword, dststr):
        return re.findall(keyword, str(dststr))

    def request(self, dsturl):
        return requests.get(dsturl, verify=False, timeout=3)

    def getphpversion(self):
        global phpversion
        phpversion = self.refindall("PHP\/\S*", GetResponse.getbynormalheaders(self))
        if phpversion:
            self.outputphp("PHP版本信息（GetByNormal）:",phpversion)
        else:
            phpversion = self.refindall("PHP\/\S*", GetResponse.getbynormaltext(self))
            if phpversion:
                self.outputphp("PHP版本信息（GetByNormal）:", phpversion)
            else:
                phpversion = self.refindall("PHP Version\s\S\S\S\S\S\S\S", GetResponse().getbyphpinfo())
                if phpversion:
                    self.outputphp("PHP版本信息（GetByphpinfo.php）:", phpversion)
                else:
                    phpversion = self.refindall("PHP Version\s\S\S\S\S\S\S\S", GetResponse().getbyinfo())
                    if phpversion:
                        self.outputphp("PHP版本信息（GetByinfo.php）:", phpversion)

    def getapacheversion(self):
        global apacheversion
        apacheversion = self.refindall("Apache\/\S*", GetResponse.getbynormalheaders(self))
        if apacheversion:
            self.outputphp("Apache版本信息（GetByNormal）:",apacheversion)
        else:
            apacheversion = self.refindall("Apache\/\S*", GetResponse.getbynormaltext(self))
            if apacheversion:
                self.outputphp("Apache版本信息（GetByNormal）:", apacheversion)
            else:
                apacheversion = self.refindall("Apache\/\S*", GetResponse().getbyphpinfo())
                if apacheversion:
                    self.outputphp("Apache版本信息（GetByphpinfo.php）:", apacheversion)
                else:
                    apacheversion = self.refindall("Apache\/\S*", GetResponse().getbyinfo())
                    if phpversion:
                        self.outputphp("Apache版本信息（GetByinfo.php）:", apacheversion)

    def getnginxversion(self):
        global nginxversion
        nginxversion = self.refindall("PHP\/\S*", GetResponse.getbynormalheaders(self))
        if nginxversion:
            self.outputphp("Nginx版本信息（GetByNormal）:",nginxversion)
        else:
            nginxversion = self.refindall("PHP\/\S*", GetResponse.getbynormaltext(self))
            if nginxversion:
                self.outputphp("Nginx版本信息（GetByNormal）:", nginxversion)
            else:
                nginxversion = self.refindall("PHP Version\s\S\S\S\S\S\S\S", GetResponse().getbyphpinfo())
                if nginxversion:
                    self.outputphp("Nginx版本信息（GetByphpinfo.php）:", nginxversion)
                else:
                    nginxversion = self.refindall("PHP Version\s\S\S\S\S\S\S\S", GetResponse().getbyinfo())
                    if phpversion:
                        self.outputphp("Nginx版本信息（GetByinfo.php）:", nginxversion)


    def gettomcatversion(self):
        global tomcatversion
        tomcatversion = self.refindall("Apache Tomcat\S\S\S\S\S\S\S", GetResponse.getby404headers(self))
        if tomcatversion:
            self.outputphp("Tomcat版本信息（GetBy404）:",tomcatversion)
        else:
            tomcatversion = self.refindall("Apache Tomcat\S\S\S\S\S\S\S", GetResponse.getby404text(self))
            if tomcatversion:
                self.outputphp("Tomcat版本信息（GetBy404）:", tomcatversion)
            else:
                tomcatversion = self.refindall("Apache Tomcat\S\S\S\S\S\S\S", GetResponse().getbyrange())#因为getbyrange（）中没有使用 self.xxx，所以不需要传递 self
                if tomcatversion:
                    self.outputphp("Tomcat版本信息（GetByBadRange）:", tomcatversion)
                else:
                    tomcatversion = self.refindall("Apache Tomcat\S\S\S\S\S\S\S", GetResponse().getbyPut())
                    if tomcatversion:
                        self.outputphp("Tomcat版本信息（GetByMethonPut）:", tomcatversion)


yy = IsUrlOk()
yy.isurlok(targeturl)
xx = GetVersion()
xx.getphpversion()
xx.getapacheversion()
xx.gettomcatversion()

