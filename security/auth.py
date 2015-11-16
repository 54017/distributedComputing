import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import os.path
from pymongo import MongoClient
import hashlib

from tornado.options import define, options
define("port", default=80, help="run on the given port", type=int)


def role(array):
    def _role(method):
        def __role(self, *args, **kwargs):
            type = self.get_secure_cookie("type")
            print "type: ", type 
            print "array", array
            if type in array:
                return method(self, *args, **kwargs)
            else:
                self.write("no right to access")
        return __role
    return _role

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
                self.set_secure_cookie("type", user["type"])
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

class vipHandler(tornado.web.RequestHandler):
    @role(['vip'])
    def get(self):
        self.render('vip.html', user=self.current_user)

class adminHandler(tornado.web.RequestHandler):
    @role(['vip', 'admin'])
    def get(self):
        self.render('admin.html', user=self.current_user)

class userHandler(tornado.web.RequestHandler):
    @role(['vip', 'user'])
    def get(self):
        self.render('user.html', user=self.current_user)

class guestHandler(tornado.web.RequestHandler):
    @role(['vip', 'user', 'admin', 'guest'])
    def get(self):
        self.render('guest.html', user=self.current_user)

class LogoutHandler(BaseHandler):
    def get(self):
        if (self.get_argument("logout", None)):
            self.clear_cookie("username")
            self.redirect("/")

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
        (r'/vip', vipHandler),
        (r'/admin', adminHandler),
        (r'/user', userHandler),
        (r'/guest', guestHandler)
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()