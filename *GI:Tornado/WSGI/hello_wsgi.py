from cgi import parse_qs

def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return '<h1>Hello, %s!</h1>' % (parse_qs(environ['QUERY_STRING']).get('user', [''])[0] or 'web')