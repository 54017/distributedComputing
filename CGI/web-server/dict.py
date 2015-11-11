import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.wsgi
import wsgiref.simple_server



dist = {}

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/(\w+)", WordHandler)]
        global dict
        f = open('dict.txt')
        line = f.readline()
        while line:
        	key = line.strip('\n')
        	line = f.readline()
        	global dist
        	line.strip('\n')
        	dist[key] = line
        	line = f.readline()
        tornado.web.Application.__init__(self, handlers, debug=True)

class WordHandler(tornado.web.RequestHandler):
    def get(self, word):
    	global dist
    	definition = dist.get(word)
    	if definition:
    		print definition
    		self.write(definition)
    	else:
    		self.write('no definition found')
    def post(self, word):
    	definition = self.get_argument("definition")
        global dist
    	original_definition = dist.get(word)
        dist[word] = definition
        

wsgi_app = tornado.wsgi.WSGIAdapter(Application())
