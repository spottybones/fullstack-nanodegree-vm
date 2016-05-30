from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi, re

# set up a database session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            print('path={}'.format(self.path))
            path_parts = self.path.split('/')
            print('path_parts={}'.format(path_parts))

            if path_parts[-1] == 'restaurants':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body><h1>Hello!</h1>"
                output += '<a href="/restaurants/new">Add New Restaurant</a>'
                output += "<ul>"

                restaurants = session.query(Restaurant).all()
                for restaurant in restaurants:
                    output += " <li>{}<br>".format(restaurant.name)
                    output += '  <a href="/restaurants/{}/edit">Edit</a><br>'.format(restaurant.id)
                    output += '  <a href="/restaurants/{}/delete">Delete</a><br>'.format(restaurant.id)
                    output += " </li>"

                output += "</ul>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            # if self.path.endswith('/restaurants/new'):
            if '/'.join(path_parts) == '/restaurants/new':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body><p>Create a New Restaurant</p><p><a href='/restaurants'>Back to Restaurant List</a>"
                output += """<form method='POST' enctype='multipart/form-data' action='new_restaurant'>
                            <h2>Enter Name of New Restaurant</h2>
                            <input name='restaurant_name' type='text'>
                            <input type='submit' value='Submit'>
                            </form>"""
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            rest_edit = re.match(r'/restaurants/(\d+)/edit$', self.path)
            if rest_edit:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                my_restaurant = session.query(Restaurant).get(int(rest_edit.group(1)))

                output = ""
                output += "<html><body><h1>Edit Restaurant</h1>"
                output += '<p><a href="/restaurants">Back to Restaurant List</a>'
                output += """<form method='POST' enctype='multipart/form-data'>
                            <h2>Enter New Name of Restaurant</h2>
                            <input name='name' type='text' value='{0}'>
                            <input name='id' type='hidden' value='{1}'>
                            <input type='submit' value='Submit'>
                            </form>""".format(my_restaurant.name, my_restaurant.id)
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return


            # if self.path.endswith('/hola'):
            if path_parts[-1] == 'hola':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body><p>&#161Hola!</p><p><a href='/hello'>Back to Hello</a>"
                output += """<form method='POST' enctype='multipart/form-data' action='hello'>
                            <h2>What would you like me to say?</h2>
                            <input name='message' type='text'>
                            <input type='submit' value='Submit'>
                            </form>"""
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

        except:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/hello'):
                self.send_response(301)
                self.end_headers()

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')

                output = ""
                output += "<html><body>"
                output += "<h2>Okay, how about this:</h2>"
                output += "<h1>%s</h1>" % messagecontent[0]
                output += """<form method='POST' enctype='multipart/form-data' action='hello'>
                            <h2>What would you like me to say?</h2>
                            <input name='message' type='text'>
                            <input type='submit' value='Submit'>
                            </form>"""
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith('/new_restaurant'):
                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_name = fields.get('restaurant_name')[0]
                    new_restaurant = Restaurant(name=restaurant_name)
                    session.add(new_restaurant)
                    session.commit()

                print('New restaurant: {} added.'.format(new_restaurant.name))
                return

            rest_edit = re.match(r'/restaurants/(\d+)/edit$', self.path)
            if rest_edit:
                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()

                my_restaurant = session.query(Restaurant).get(int(rest_edit.group(1)))

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    my_restaurant.name = fields.get('name')[0]
                    session.add(my_restaurant)
                    session.commit()

                print('Restaurant name: {} updated.'.format(my_restaurant.name))
                return

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()


if __name__ == '__main__':
    main()
