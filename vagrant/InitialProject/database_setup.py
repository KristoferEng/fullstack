import sys #Provides functions and variables to manipulate the Python run time environment.

from sqlalchemy import Column, ForeignKey, Integer, String #Imports classes from sqlalchemy to use below.
from sqlalchemy.ext.declarative import declarative_base #Imports classes to use in configuration and class code.
from sqlalchemy.orm import relationship #Imports class for foreign key relationships.
from sqlalchemy import create_engine #Imports class to configure code.

Base = declarative_base() #Makes instance of declarative base to let sqlalchemy know that they represent tables.


class Restaurant(Base): #Argument in class extends the Base class
    __tablename__ = 'restaurant' #From declarative_base #Lets sqlalchemy know the variable that will be used to refer to table.

    id = Column(Integer, primary_key=True) #Must be unique key
    name = Column(String(250), nullable=False) #250 is maximum string length. #Nullable = false means that it must have a value in order for row to be created.
    #id = Column(Integer, primary_key=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class MenuItem(Base): #Argument in class extends the Base class
    __tablename__ = 'menu_item'

    name = Column(String(80), nullable=False) #Nullable = false means that it must have a value in order for row to be created.
    id = Column(Integer, primary_key=True) #Must be unique key
    description = Column(String(250))
    price = Column(String(8))
    course = Column(String(250))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id')) #ForeignKey is used to reference a row in a different table.
    restaurant = relationship(Restaurant) #Relationship one table has to another

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
        }


engine = create_engine('sqlite:///restaurantmenu.db') #Creates instance of create_engine and points to database.


Base.metadata.create_all(engine) #Goes into database and creates the tables with the "Base".
