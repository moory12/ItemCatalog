#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash, make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Catalog, Item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# homepage html


@app.route('/')
@app.route('/catalog')
def homepage():
    catalog = session.query(Catalog).all()
    item = session.query(Item).all()
    if 'username' in login_session:
        return render_template(
            'catalog.html',
            catalog=catalog,
            len=len(item),
            item=item,
            button=True)
    else:
        return render_template(
            'catalog.html',
            catalog=catalog,
            len=len(item),
            item=item)

# catalog html page


@app.route('/catogary/<int:catalog_id>/')
def catogary(catalog_id):
    catogary = session.query(Item).filter_by(catalog_id=catalog_id).all()
    if 'username' in login_session:
        return render_template('item.html', catalog=catogary, button=True)
    else:
        return render_template('item.html', catalog=catogary)

# item html page


@app.route('/catogary/item/<int:item_id>/')
def item(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    if 'username' in login_session:
        return render_template('description.html', item=item, button=True)
    else:
        return render_template('description.html', item=item)

# this code from udacity


@app.route('/login')
def loginButton():
    state = ''.join(random.choice(string.ascii_uppercase + string.
                                  digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# this code from udacity


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:'
    output += '150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None

# to disconnect a user from google sign in


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?'
    url += 'token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response

# create item method


@app.route('/Items/createItem', methods=['GET', 'POST'])
def createItem():
    if 'username' not in login_session:
        redirect(url_for('loginButton'))
    if request.method == 'POST':
        user = session.query(User).filter_by(id=login_session['user_id']).one()
        catalog = session.query(Catalog).filter_by(
            name=request.form['options']).one()
        item = Item(
            name=request.form['name'],
            description=request.form['description'],
            catalog=catalog,
            user=user)
        session.add(item)
        session.commit()
        return redirect(url_for('homepage'))
    else:
        return render_template('createItem.html')

# edit item method


@app.route('/Items/editItem/<int:item_id>', methods=['GET', 'POST'])
def editItem(item_id):
    if 'username' not in login_session:
        redirect(url_for('loginButton'))
    if request.method == 'POST':
        item = session.query(Item).filter_by(id=item_id).one()
        if login_session['user_id'] != item.user_id:
            output = "<script>function myFunction() {alert('You are not"
            output += "authorized to edit this item."
            output += "Please create your own itemin order to edit.');"
            output += "}</script><body onload='myFunction()'>"
            return output
        else:
            if request.form['name']:
                item.name = request.form['name']
            if request.form['description']:
                item.description = request.form['description']
            session.add(item)
            session.commit()
            return redirect(url_for('homepage'))
    else:
        item = session.query(Item).filter_by(id=item_id).one()
    return render_template('editItem.html', item=item)

# delete item method


@app.route('/Items/deleteItem/<int:item_id>', methods=['GET', 'POST'])
def deleteItem(item_id):
    if 'username' not in login_session:
        redirect(url_for('loginButton'))
    if request.method == 'POST':
        item = session.query(Item).filter_by(id=item_id).one()
        if login_session['user_id'] != item.user_id:
            output = "<script>function myFunction() {alert('You are not"
            output += "authorized to edit this item."
            output += "Please create your own itemin order to edit.');"
            output += "}</script><body onload='myFunction()'>"
            return output
        else:
            session.delete(item)
            session.commit()
            return redirect(url_for('homepage'))
    else:
        item = session.query(Item).filter_by(id=item_id).one()
    return render_template('deleteItem.html', item=item)

# json method to generate the json file


@app.route('/catalog/json')
def catalogJSON():
    catalog = session.query(Catalog).all()
    item = session.query(Item).all()
    x = []
    for i in catalog:
        x.append(i.serialize)
        for j in item:
            if j.catalog_id == i.id:
                x.append(j.serialize)
    return jsonify(catalog=x)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
