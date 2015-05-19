from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

# Initialize the database to work with and bind it to Base
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

# Create a new session to access and update the database
DBSession = sessionmaker(bind=engine)
session = DBSession()


def getUserID(email):
    """Helper method for getting user ID."""

    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def createUser(login_session_2):
    """Helper method for creating user ID."""

    newUser = User(name=login_session_2['username'], email=login_session_2[
                   'email'], picture=login_session_2['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session_2['email']).one()
    return user.id


def getUserInfo(user_id):
    """Helper method for getting user info."""
    user = session.query(User).filter_by(id=user_id).one()
    return user
