import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)


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
        

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()