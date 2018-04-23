from flask import Flask, render_template, url_for, request
from flask import flash, redirect, jsonify


from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from functools import wraps

import os

from database_setup import Base, Catalog, Item, User

from flask import session as login_session


import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
import requests

from flask import make_response

import ssl

# Defining app
app = Flask(__name__)

# get client ID
CLIENT_ID = json.loads(
	open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "catalog-197420"

# Create engine
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

# Defining DB session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Defining login route
@app.route('/login')
def login():
    # Create Anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    # set login session state equals state value
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps(
            'Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secret.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps(
                'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http(disable_ssl_certificate_validation=True)
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(
            result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's. "), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session["picture"]
    output += ' "style = "width: 300px; height: 300px; '
    output += 'border-radius: 150px; '
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User helper functions
# create user
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# get user info
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    newUser = User(name=login_session["username"],
                   email=login_session["email"],
                   picture=login_session["picture"])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Defining disconnect route
@app.route('/disconnect')
def disconnect():
    # Check provider in session
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            if 'gplus_id' in login_session:
                del login_session['gplus_id']
            if 'credentials' in login_session:
                del login_session['credentials']
        # delete values in session
        if 'username' in login_session:
            del login_session['username']
        if 'email' in login_session:
            del login_session['email']
        if 'picture' in login_session:
            del login_session['picture']
        if 'user_id' in login_session:
            del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        # redirect
        return redirect(url_for('catalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('catalog'))


@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps(
                'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" % access_token
    h = httplib2.Http(disable_ssl_certificate_validation=True)
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps(
            'successfully disconnect'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Defining JSON APIs
@app.route('/catalog.json/')
def catalogJSON():
    category = session.query(Catalog).all()
    return jsonify(category=[c.serialize for c in category])


@app.route('/catalog/<int:category_id>/items/json')
def itemsJSON(category_id):
    items = session.query(Item).all()
    return jsonify(category=[i.serialize for i in items])


# Defining Routes
# Categories Routes
@app.route('/')
@app.route('/catalog/')
def catalog():
    catalog = session.query(Catalog).all()
    last = session.query(Item).order_by(desc(Item.created_date)).limit(10)
    return render_template('catalog.html', catalog=catalog, last=last)


# Items Routes
@app.route('/catalog/<int:category_id>/items/')
def items(category_id):
    category = session.query(Catalog).filter_by(id=category_id).one()
    catalog = session.query(Catalog).all()
    items = session.query(Item).filter_by(catalog_id=category_id).all()
    if 'username' not in login_session:
        return redirect('/login')
    else:
        return render_template('items.html',
                               items=items,
                               category=category,
                               catalog=catalog)


@app.route('/catalog/<int:category_id>/items/new/', methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Catalog).filter_by(id=category_id).one()
    categories = session.query(Catalog).all()
    if request.method == 'POST':
        item = Item(name=request.form['newItem'],
                    img_url=request.form['imgurl'],
                    catalog_id=request.form['comp_select'],
                    user_id=login_session['user_id'])
        session.add(item)
        flash('New item %s successfully created' % item.name)
        session.commit()
        return redirect(url_for('items', category_id=category.id))
    else:
        return render_template('newitem.html',
                               category=category,
                               data=[{'cat': 2, 'name': 'Adventure'},
                                     {'cat': 3, 'name': 'Action'},
                                     {'cat': 4, 'name': 'RPG'},
                                     {'cat': 5, 'name': 'Simulator'},
                                     {'cat': 6, 'name': 'Sport'},
                                     {'cat': 7, 'name': 'Stealth'}])


@app.route('/catalog/<int:category_id>/items/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Catalog).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    if item.user_id != login_session['user_id']:
        return '<script>function myFunction() {'
        'alert("You are not authorized to edit menu items'
        'to this restaurant. Please create your own '
        'restaurant in order to edit items.")'
        ';}</script><body onload="myFunction()">'
    if request.method == 'POST':
        if request.form['editItem']:
            item.name = request.form['editItem']
        if request.form['editDescription']:
            item.description = request.form['editDescription']
        if request.form['imgurl']:
            item.img_url = request.form['imgurl']
        if request.form['comp_select']:
            item.catalog_id = request.form.get('comp_select')
        session.add(item)
        flash('item %s successfully edited' % item.name)
        session.commit()
        return redirect(url_for('items', category_id=category.id))
    else:
        return render_template('edititem.html',
                               category=category,
                               item=item,
                               data=[{'cat': 2, 'name': 'Adventure'},
                                     {'cat': 3, 'name': 'Action'},
                                     {'cat': 4, 'name': 'RPG'},
                                     {'cat': 5, 'name': 'Simulator'},
                                     {'cat': 6, 'name': 'Sport'},
                                     {'cat': 7, 'name': 'Stealth'}])


@app.route('/catalog/<int:category_id>/items/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Catalog).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    if item.user_id != login_session['user_id']:
        return '<script>function myFunction() {'
        'alert("You are not authorized to delete this item.'
        'Please create your own item in order to delete.")'
        ';}</script><body onload="myFunction()">'
    if request.method == 'POST':
        session.delete(item)
        flash('Item %s successfully deleteded' % item.name)
        session.commit()
        return redirect(url_for('items', category_id=category.id))
    else:
        return render_template('deleteitem.html', category=category, item=item)


@app.route('/catalog/<int:category_id>/items/<int:item_id>/')
def showItem(category_id, item_id):
    category = session.query(Catalog).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(catalog_id=category.id).all()
    item = session.query(Item).filter_by(id=item_id).one()
    if 'username' not in login_session:
        return render_template('publicshowitem.html',
                               category=category,
                               item=item,
                               items=items)
    else:
        return render_template('showitem.html',
                               category=category,
                               item=item,
                               items=items)


# Defining port and secret key
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
