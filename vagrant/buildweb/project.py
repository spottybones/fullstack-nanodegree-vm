from flask import Flask
app = Flask(__name__)

# set up a database session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/hello')
def HelloWorld():
    restaurant = session.query(Restaurant).first()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    output = "<h1>Menu Items at {}</h1>".format(restaurant.name)
    for item in items:
        output += "<p>{}<br>".format(item.name)
        output += "{}<br>".format(item.price)
        output += "{}</p>\n".format(item.description)

    return output


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)