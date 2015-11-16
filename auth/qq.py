import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import os.path
from pymongo import MongoClient
import hashlib
import httpclient
import urllib
import json



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
    @tornado.web.authenticated
    def get(self):
        self.render('index.html', user=self.current_user)

class LogoutHandler(BaseHandler):
    def get(self):
        if (self.get_argument("logout", None)):
            self.clear_cookie("username")
            self.redirect("/")

class qqHandler(tornado.web.RequestHandler):
    def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch("https://graph.qq.com/oauth2.0/authorize?" + urllib.urlencode({}), callback=self.on_response)

    def on_response(self, response):


if __name__ == "__main__":
    tornado.options.parse_command_line()

    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "login_url": "/login",
        "debug": True
    }

    application = tornado.web.Application([
        (r'/', WelcomeHandler),
        (r'/login', LoginHandler),
        (r'/logout', LogoutHandler),
        (r'/qq', qqHandler)
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(application)
    tornado.ioloop.IOLoop.instance().start()