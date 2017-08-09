from flask import Flask
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route('/')
def welcome():
    return "Welcome to Yelp!"

@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id)
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    output = ""
    for item in items:
        output += "<b>{}</b> - {}</br>".format(item.name, item.description)
        output += "{}</br>".format(item.price)
        output += "</br></br>"
    return output

@app.route('/restaurants/new/')
def newMenuItem(restaurant_id):
    return "page to create a new menu item."

@app.route('/restaurants/<int:restaurant_id>/edit/')
def editMenuItem(restaurant_id, menu_id):
    return "page to edit a new menu item."

@app.route('/restaurants/<int:restaurant_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
    return "page to delete a menu item."

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
