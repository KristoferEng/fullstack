from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from db_helper import getUserID, createUser, getUserInfo
from flask import session as login_session_2
import random
import string

# Import for GConnect
from flask import make_response, flash
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

# Import for Login Required Decorator
from functools import wraps
from flask import g


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session_2:
            flash("You are not signed in. Sign in to access")
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function

# Initialize the database to work with and bind it to Base
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

# Create a new session to access and update the database
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

# Save for later use
CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']


@app.route('/')
@app.route('/catalog')
def catalogHome():
    """Shows home page with all categories and 10 latest items."""

    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.id.desc()).limit(10).all()

    # Check if user logged in to display public or restricted home page
    if 'username' not in login_session_2:
        return render_template('publicHome2.html',
                               categories=categories, items=items)
    else:
        return render_template('home2.html',
                               categories=categories, items=items)


@app.route('/login')
def showLogin():
    """Creates antiforgery session token and sets it to state."""

    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session_2['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Connects to Google + using hybrid authentication flow."""

    # Validate state token
    if request.args.get('state') != login_session_2['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data

    # Upgrade the authorization code into a credentials object
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()

    # Create JSON get request
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session_2.get('credentials')
    stored_gplus_id = login_session_2.get('gplus_id')

    # Check if user is connected
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session_2['credentials'] = credentials.to_json()
    login_session_2['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # Set user info to login_session_2
    login_session_2['username'] = data['name']
    login_session_2['picture'] = data['picture']
    login_session_2['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session_2['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session_2)
    login_session_2['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session_2['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session_2['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session_2['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """Disconnects and logs out current Google + user."""

    # Only disconnect a connected user.
    credentials = login_session_2.get('credentials')

    # Check if connected
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get access_token
    access_token = json.loads(credentials)['token_response']['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token

    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # Check if failed to revoke token
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/disconnect')
def disconnect():
    """Disconnect method."""

    # Delete session if logged in
    if 'provider' in login_session_2:
        if login_session_2['provider'] == 'google':
            gdisconnect()
            del login_session_2['gplus_id']
            del login_session_2['credentials']
        del login_session_2['username']
        del login_session_2['email']
        del login_session_2['picture']
        del login_session_2['user_id']
        del login_session_2['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('catalogHome'))
    else:
        flash("You were not logged in")
        return redirect(url_for('catalogHome'))


@app.route('/catalog/new', methods=["GET", "POST"])
@login_required
def newCategory():
    """Creates a new category in the database."""

    # Check if POST method and add new category
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               user_id=login_session_2['user_id'])
        session.add(newCategory)
        session.commit()
        flash('New Category %s Successfully Created' % newCategory.name)
        return redirect(url_for('catalogHome'))
    else:
        return render_template('newCategoryPage.html')


@app.route('/catalog/<int:category_id>/<category_name>/items')
def showCategoryItems(category_id, category_name):
    """Shows a category's items in the database."""

    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=category_id).all()

    # Check if logged in
    if 'username' not in login_session_2:
        return render_template('publicShowCategoryItemsPage.html',
                               categories=categories, category_id=category_id,
                               category_name=category_name.title(),
                               items=items)
    else:
        return render_template('showCategoryItemsPage.html',
                               categories=categories, category_id=category_id,
                               category_name=category_name.title(),
                               items=items)


@app.route('/catalog/<int:category_id>/<category_name>/edit',
           methods=["GET", "POST"])
@login_required
def editCategory(category_id, category_name):
    """Edits a category in the database."""

    categoryToEdit = session.query(Category).filter_by(id=category_id).one()

    # Check if user is user that created category
    if categoryToEdit.user_id != login_session_2['user_id']:
        return "<script>function myFunction() {alert(\
               'You are not authorized to edit this category.'\
               );}</script><body onload='myFunction()''>"

    # Check if method is POST and edit category name
    if request.method == 'POST':
        editCat = session.query(Category).filter_by(id=category_id).one()
        editCat.name = request.form['name']
        session.add(editCat)
        session.commit()
        flash("The category has been edited")
        return redirect(url_for('catalogHome'))
    return render_template('editCategoryPage.html',
                           category_id=category_id,
                           category_name=category_name)


@app.route('/catalog/<int:category_id>/<category_name>/delete',
           methods=["GET", "POST"])
@login_required
def deleteCategory(category_id, category_name):
    """Deletes a category and all its items in the database."""

    categoryToDelete = session.query(Category).filter_by(id=category_id).one()

    # Check if user is user that created category
    if categoryToDelete.user_id != login_session_2['user_id']:
        return "<script>function myFunction() {alert(\
               'You are not authorized to delete this category.'\
               );}</script><body onload='myFunction()''>"

    # Check if method is POST and delete category
    if request.method == 'POST':
        items = session.query(Item).filter_by(category_id=category_id).all()
        for item in items:
            session.delete(item)
        category = session.query(Category).filter_by(id=category_id).one()
        session.delete(category)
        session.commit()
        flash("The category has been deleted")
        return redirect(url_for('catalogHome'))
    else:
        return render_template('deleteCategoryPage.html',
                               category_id=category_id,
                               category_name=category_name)


@app.route('/catalog/<int:category_id>/<category_name>/new',
           methods=["GET", "POST"])
@login_required
def newItem(category_id, category_name):
    """Creates a new items in the database."""

    categoryForItem = session.query(Category).filter_by(id=category_id).one()

    # Check if user is user that created category
    if categoryForItem.user_id != login_session_2['user_id']:
        return "<script>function myFunction() {alert(\
               'You are not authorized to create an item in this category.'\
               );}</script><body onload='myFunction()''>"
    categories = session.query(Category).all()

    # Check if method is POST and add new item
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=category_id)
        session.add(newItem)
        session.commit()
        flash("The item has been added")
        return redirect(url_for('showCategoryItems', category_id=category_id,
                                category_name=category_name))
    else:
        return render_template('newItemPage.html',
                               category_id=category_id,
                               category_name=category_name)


@app.route(
    '/catalog/<int:category_id>/<category_name>/<int:item_id>/<item_name>')
def showItem(category_id, category_name, item_id, item_name):
    """Shows an items in the database."""

    item = session.query(Item).filter_by(id=item_id).one()

    # Check if logged in
    if 'username' not in login_session_2:
        return render_template('publicShowItemPage.html',
                               category_id=category_id,
                               category_name=category_name, item_id=item_id,
                               item_name=item_name, item=item)
    else:
        return render_template('showItemPage.html', category_id=category_id,
                               category_name=category_name, item_id=item_id,
                               item_name=item_name, item=item)


@app.route('/catalog/<int:category_id>/<category_name>/<int:item_id>/edit',
           methods=["GET", "POST"])
@login_required
def editItem(category_id, category_name, item_id):
    """Edits an item in the database."""

    categoryForItem = session.query(Category).filter_by(id=category_id).one()

    # Check if user is user that created category
    if categoryForItem.user_id != login_session_2['user_id']:
        return "<script>function myFunction() {alert(\
               'You are not authorized to edit an item in this category.'\
               );}</script><body onload='myFunction()''>"
    categories = session.query(Category).all()
    item = session.query(Item).filter_by(id=item_id).one()

    # Check if method is POST and edit item
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.category_id = request.form['category_id']
        print request.form['category_id'] + "-----"
        session.add(item)
        session.commit()
        flash("The item has been edited")
        return redirect(url_for('showItem',
                        category_id=category_id, category_name=category_name,
                        item_id=item.id, item_name=item.name))
    else:
        return render_template('editItemPage.html',
                               category_id=category_id,
                               category_name=category_name, item_id=item_id,
                               item=item, categories=categories)


@app.route('/catalog/<int:category_id>/<category_name>/<int:item_id>/delete',
           methods=["GET", "POST"])
@login_required
def deleteItem(category_id, category_name, item_id):
    """Deletes an item in the database."""

    categoryForItem = session.query(Category).filter_by(id=category_id).one()

    # Check if user is user that created category
    if categoryForItem.user_id != login_session_2['user_id']:
        return "<script>function myFunction() {alert(\
               'You are not authorized to delete an item in this category.'\
               );}</script><body onload='myFunction()''>"

    # Check if method is POST and delete item
    if request.method == 'POST':
        item = session.query(Item).filter_by(id=item_id).one()
        session.delete(item)
        session.commit()
        flash("The item has been deleted")
        return redirect(url_for('showCategoryItems', category_id=category_id,
                                category_name=category_name))
    else:
        return render_template('deleteItemPage.html', category_id=category_id,
                               category_name=category_name, item_id=item_id)


@app.route('/catalog/json')
def catalogJSON():
    """Provides JSON for all categories in the database."""

    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/catalog/<int:category_id>/<category_name>/json')
def categoryJSON(category_id, category_name):
    """Provides JSON for all items in a category in the database."""

    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(items_in_category=[i.serialize for i in items])


@app.route('/catalog/<int:category_id>/<category_name>/<int:item_id>/\
           <item_name>/json')
def itemJSON(category_id, category_name, item_id, item_name):
    """Provides JSON for an item in a category in the database."""

    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(item=[item.serialize])

if __name__ == '__main__':
    """Checks if it is called and sets the port."""

    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
