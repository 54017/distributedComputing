# -*- coding: utf-8 -*-
import os
import tornado.web
import tornado.wsgi
import urllib2
import urlparse
import sae
import wsgiref.handlers
import sae.kvdb
import hashlib
import urllib
import json
import sae
import wsgiref.handlers
import sae.kvdb
import re




class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")

class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        name = self.get_argument("username", None)
        password = self.get_argument("password", None)
        conn = MongoClient("localhost", 27017)
        self.db = conn["users"]
        user = self.db.validUsers.find_one({"name alias": name})
        if user:
            m = hashlib.md5()
            m.update(password)
            if user["password"] == m.hexdigest():
                self.set_secure_cookie("username", name)
                self.redirect("/")
            else:
                self.set_header("Content-Type", "text/plain")
                self.write("error")
        else:
            self.redirect("/login")

class WelcomeHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.render('index.html', user=self.current_user)
            return
        code = self.get_argument("code", None)
        state = self.get_argument("state", None)
        m = hashlib.md5()
        m.update("auth")
        if (state == None or state != m.hexdigest() or code == None):
            self.redirect("/login")
            return
        response = urllib2.urlopen("https://graph.qq.com/oauth2.0/token?" + urllib.urlencode({"code": code, "grant_type": "authorization_code", "client_id": 101265047, "client_secret": "d7318d95864a9535b2283eb21278469f", "redirect_uri": "http://liyiqi.sinaapp.com"}))
        params = urlparse.parse_qs(response.read(), True)
        access_token = params["access_token"][0]
        second_response = urllib2.urlopen("https://graph.qq.com/oauth2.0/me?access_token=" + access_token)
        reg = re.compile(r'callback\( | \);')
        openid = json.loads(reg.sub('', second_response.read()))["openid"]
        third_response = urllib2.urlopen("https://graph.qq.com/user/get_user_info?" + urllib.urlencode({"access_token": access_token, "oauth_consumer_key": 101265047, "openid": openid}))
        third_response = json.loads(third_response.read())
        name = third_response["nickname"]
        self.set_secure_cookie("username", name)
        self.render('index.html', user=name)
        
class LogoutHandler(BaseHandler):
    def get(self):
        if (self.get_argument("logout", None)):
            self.clear_cookie("username")
            self.redirect("/")

class qqHandler(tornado.web.RequestHandler):
    def get(self):
        m = hashlib.md5()
        m.update("auth")
        state = m.hexdigest()
        self.redirect("https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101265047&redirect_uri=http://liyiqi.sinaapp.com&state=" + state)


settings = {
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
    "login_url": "/login",
    "debug": True
}

app = tornado.wsgi.WSGIApplication([
    (r'/', WelcomeHandler),
    (r'/login', LoginHandler),
    (r'/logout', LogoutHandler),
    (r'/qq', qqHandler)
], **settings)

application = sae.create_wsgi_app(app)