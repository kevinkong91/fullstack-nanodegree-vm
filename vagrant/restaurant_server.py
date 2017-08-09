from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith('/restaurants'):
                # Return success header
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                all_restaurants = session.query(Restaurant).all()

                # Print each restaurant
                output = ""
                output += "<html><body>"
                output += "<h2>Restaurants in the known universe:</h2><ol>"
                for restaurant in all_restaurants:
                    output += "<li><h4>%s</h4>" % restaurant.name
                    output += "<a href='%s/edit'><span>Edit</span></a>" % restaurant.id
                    output += "<span> </span><a href='%s/confirm_delete'><span>Delete</span></a></li>" % restaurant.id
                output += "</ol></body></html>"
                self.wfile.write(output.encode())
                print(output)
                return

            elif self.path.endswith('/new'):
                # Return success header
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # Print out new restaurant form
                output = ""
                output += "<html><body>"
                output += "<h1>Create a New Restaurant!</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/new'>"
                output += "<input name='name' type='text'>"
                output += "<input type='submit' value='Submit'"
                output += "</form></body></html>"
                self.wfile.write(output.encode())
                return


            elif self.path.endswith('/edit'):
                # Return success header
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # Parse out the restaurant id from path
                restaurant_id = int(self.path[1:].split('/',1)[0])
                restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

                # Print out edit form
                output = ""
                output += "<html><body>"
                output += "<h2>Edit Info for %s:</h2>" % restaurant.name
                output += "<form method='POST' enctype='multipart/form-data' action='/%s/edit'>" % restaurant.id
                output += "<input name='new_name' type='text' value='%s'>" % restaurant.name
                output += "<input type='submit' value='Submit'>"
                output += "</form>"
                output += "</body></html>"
                self.wfile.write(output.encode())
                return


        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/edit'):
                # Return redirect header
                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()

                # Restaurant to edit
                restaurant_id = int(self.path[1:].split('/',1)[0])
                restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

                # Parse restaurant id from form data
                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    new_name = fields.get('new_name')
                restaurant.name = new_name

                # Save changes to db
                session.add(restaurant)
                session.commit()
                print('Sucessfully edited restaurant name to {}'.format(restaurant.name))
                return

            elif self.path.endswith('/new'):
                # Return redirect header
                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()

                # Parse new restaurant's attributes
                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_name = fields.get('name')

                # Save changes to db
                new_restaurant = Restaurant(name=restaurant_name)
                session.add(new_restaurant)
                session.commit()
                print('Successfully added new restaurant with name: {}'.format(new_restaurant.name))
                return

        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print("Web server running on port %s..." % port)
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
        server.socket.close()

if __name__ == '__main__':
    main()
