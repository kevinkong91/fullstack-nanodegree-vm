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

            


        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
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
