# -*- coding: utf-8 -*-

import sys
import re
import os
import random

from PIL import Image
from urllib.request import urlopen
from io import BytesIO
from http.server import BaseHTTPRequestHandler, HTTPServer
from bs4 import BeautifulSoup

catlist = [
    (u"。",(u"にゃ。",u"にゃあ。",u"にゃんだ。")),
    #('\n',u"にゃ\n"),
    (u"な",u"にゃ"),
    (u"ナ",u"ニァ")
]

catPicList = []

nyaList = [u"にゃ。",u"にゃあ。",u"にゃんである",u"にゃんであった",u"にゃのだ",u"にゃーーーーー"]

first = True

TMPL = """<html>
  <body>
    <h1>Proxy Server Error</h1>
    <div>response error to '%(path)s'</div>
    <div>ERROR: <b>%(error)s</b></div>
  </body>
</html>
"""
# TODO: POSTメソッドを適切に扱う ..
# TODO: utf8以外のエンコードのページも処理できるようにする <- 完了
# TODO: 画像が表示されない場合の原因を調べる <- binaryデータがunicode変換されたせい

def getNavigableStrings(soup):
  if isinstance(soup, BeautifulSoup.NavigableString):
    if type(soup) not in (BeautifulSoup.Comment,
      BeautifulSoup.Declaration) and soup.strip():
      yield soup
  elif soup.name not in ('script', 'style'):
    for c in soup.contents:
      for g in getNavigableStrings(c):
        yield g

class TransHandler(BaseHTTPRequestHandler):

    def trans(self, content):
        soup = BeautifulSoup(content,'html.parser',from_encoding='utf-8')

        for e in soup.find_all():
            if e.name not in ('script','style') and e.string:
                try:
                    #fixed_text = str(e)+u"にゃ"
                    e.replace_with(e.string+nyaList[random.randint(1,len(nyaList))-1])
                except:
                    pass

        content = soup.prettify(formatter="html")
        #print(content)
        for pair in catlist:
            modifier = pair[1]
            if isinstance(pair[1],tuple):
                modifier = pair[1][random.randint(1,len(pair[1]))-1]
            content = re.sub(pair[0], modifier, content)
        return content

    def error(self, e):
        return  TMPL % dict([("path",self.path), ("error",e)])

    def reasonEncoding(self, pipe, content):
        # エンコーディングを推定する
        enc = None
        m = re.match(".*?charset=(.*)", pipe.info().typeheader)
        if not m is None:
            enc = m.group(1)
        else:
            for line in content.splitlines():
                m = re.match(""".*<meta .*? content="text/html; charset=(.*?)".*?>""", line, re.IGNORECASE)
                if m:
                    enc = m.group(1)
            if enc is None:
                print("**ACCURACY FAILURE: ",self.path)
                enc = sys.getdefaultencoding()
        return enc
    
    def html_get(self):
        print("request:",self.path)
        #try:
        pipe = urlopen(self.path)
        content = pipe.read()
        maintype = pipe.info().get_content_maintype()
        subtype = pipe.info().get_content_subtype()

        if maintype == 'text' and subtype == 'html':
            content = content.decode('utf_8')
            content = self.trans(content)
            content = content.encode('utf_8')
        elif maintype == 'image':
            if subtype.lower() in ['jpg','jpeg','png']:
                print('--------------fdsa:'+self.path)

                # get image size
                imgfile = BytesIO(content)
                f = Image.open(imgfile)
                sz = f.size
                print(sz)

                pic = catPicList[random.randint(1,len(catPicList))-1]
                pic = pic.resize(sz)
                picBytes = BytesIO()
                pic.save(picBytes, format='PNG')
                content = picBytes.getvalue()
                #content = open(picName, 'rb').read()
        #except Exception as e:
        #    print(e)
        #    content = self.error(e)
        self.wfile.write(content)

    def createPool(self):
        self.pool = Pool()

    def do_GET(self):
        self.html_get()

if __name__ == '__main__':
    serverNum = 10000
    for root, dirs, files in os.walk("catz"):
        for f in files:
            catPicList.append(Image.open('catz/'+f))

    serv_addr = ("", serverNum)
    httpd = HTTPServer(serv_addr, TransHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
