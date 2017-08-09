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
                output = "<html><body>"
                output += "<h2>Restaurants in the known universe:</h2>"
                output += "<a href='/restaurants/new'>Add New></a><ol>"
                for restaurant in all_restaurants:
                    output += "<li><h4>%s</h4>" % restaurant.name
                    output += "<a href='%s/edit'><span>Edit</span></a>" % restaurant.id
                    output += "<span> </span><a href='/restaurants/%s/delete'><span>Delete</span></a></li>" % restaurant.id
                output += "</ol></body></html>"
                self.wfile.write(output.encode())
                return

            elif self.path.endswith('/restaurants/new'):
                # Return success header
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # Print out new restaurant form
                output = "<html><body>"
                output += "<h1>Create a New Restaurant!</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
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
                restaurant_id = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

                if restaurant:
                    # Print out edit form
                    output = "<html><body>"
                    output += "<h2>Edit Info for %s:</h2>" % restaurant.name
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % restaurant.id
                    output += "<input name='new_name' type='text' value='%s'>" % restaurant.name
                    output += "<input type='submit' value='Submit'>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output.encode())
                return

            elif self.path.endswith('/delete'):
                # Return success header
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # Parse out restaurant id
                restaurant_id = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

                if restaurant:
                    # Print out confirm delete form
                    output = "<html><body>"
                    output += "<h2>Are you sure you want to delete %s?</h2>" % restaurant.name
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % restaurant.id
                    output += "<input type='submit' value='Delete'>"
                    output += "</form></body></html>"
                    self.wfile.write(output.encode())
                return


        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/edit'):
                # Restaurant to edit
                restaurant_id = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

                # Parse restaurant id from form data
                if restaurant:
                    print restaurant.name
                    ctype, pdict = cgi.parse_header(self.headers.get('Content-type'))
                    if ctype == 'multipart/form-data':
                        fields = cgi.parse_multipart(self.rfile, pdict)
                        new_name = fields.get('new_name')[0]
                        restaurant.name = new_name

                        # Save changes to db
                        session.add(restaurant)
                        session.commit()

                        # Return redirect header
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()
                        print('Sucessfully edited restaurant name to {}'.format(restaurant.name))
                return

            elif self.path.endswith('/restaurants/new'):
                # Parse new restaurant's attributes
                ctype, pdict = cgi.parse_header(self.headers.get('Content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_name = fields.get('name')[0]

                    # Save changes to db
                    new_restaurant = Restaurant(name=restaurant_name)
                    session.add(new_restaurant)
                    session.commit()

                    # Return redirect header
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                    print('Successfully added new restaurant with name: {}'.format(new_restaurant.name))
                return

            elif self.path.endswith('/delete'):
                # Return redirect header
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

                restaurant_id = self.path.split('/')[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

                if restaurant:
                    session.delete(restaurant)
                    session.commit()
                    print('Successfully deleted new restaurant {}'.format(restaurant.name))
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
