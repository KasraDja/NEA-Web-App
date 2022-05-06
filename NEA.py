import json #Used when saving cookies
from datetime import timedelta, date #Used when adding the date of an added comment
import random as rand #Used in the generated of IDs
import sqlite3 as sql #Used to create and edit database for storing data
import SHA256_algorithm as SHA #My own file
from flask import Flask, redirect, render_template, request, session, make_response #Used for webapp
import Caesar_cipher as cipher #My own file
from MergeSort import MergeSort #My own file

databaselocation = 'NEADatabase.db'

with sql.connect(databaselocation) as conn:
    c = conn.cursor()
    SQLScript = open('DatabaseCreationScript.sql')
    SQLScript  = SQLScript.read()
    c.executescript(SQLScript)

webapp = Flask(__name__)
webapp.permanent_session_lifetime = timedelta(days=7)
webapp.secret_key = '3631D8112475DE2EBD867B73ABBA7F0B8EB01083A58E6934DD74A8109AFBB51F'
list_of_cates = ['Mathematics', 'Physics', 'Computer Science', 'Biology', 'Chemistry', 'Engineering', 'Medicine']

@webapp.route('/')
def home():
    return redirect('/login')

@webapp.route('/signup', methods = ['POST', 'GET'])
def registration():
    if request.method == 'POST':
        email = cipher.encrypt(request.form['email'])
        username = cipher.encrypt(request.form['username'])
        passw = request.form['password']
        firstname = cipher.encrypt(request.form['firstname'])
        lastname = cipher.encrypt(request.form['surname'])
        with sql.connect(databaselocation) as conn:
            c = conn.cursor()
            c.execute('SELECT user_email FROM user WHERE user_email = (?)', (email,))
            email_check = c.fetchone()
            c.execute('SELECT username FROM user WHERE username = (?)', (username,))
            Username_check = c.fetchone()
            if email_check:
                return render_template('NEA_signup.html', email_conf = 'Email address already associated with an account')
            if Username_check:
                return render_template('NEA_signup.html', username_conf = 'Username already in use')
            else: #
                salt, pepper = saltandpeppergenerator()
                passhash = SHA.SHA(passw+salt+pepper)
                user_id = generate_id('user') #https://www.youtube.com/watch?v=gocwRvLhDf8&t=190s&ab_channel=TomScott done based off this video
                c.execute('INSERT INTO user (user_id, user_firstname, user_surname, user_email, username, user_passSalt, user_passhash) VALUES (?,?,?,?,?,?,?)', 
                            (user_id, firstname, lastname, email, username, salt, passhash))
            return redirect('/login')
    else:
        if "user_id" in session and request.cookies.get('categories'):
            return redirect('/homepage')
        elif not request.cookies.get('categories') and "user_id" in session:
            user_id = session.get('user_id')
            categories = fetchcategoriesnweight(user_id)
            resp = cookie(categories, '/homepage')
            return resp
        return render_template('NEA_signup.html')

@webapp.route('/login', methods = ['POST','GET'])
def login():
    if 'user_id' in session and request.cookies.get('categories'):
        return redirect('/homepage')
    elif request.method == 'POST':
        user = cipher.encrypt(request.form['user'])
        passw = request.form['password']
        with sql.connect(databaselocation) as conn:
            c = conn.cursor()
            c.execute('SELECT user_email FROM user WHERE user_email = (?)', (user,))
            email_check = c.fetchone()
            c.execute('SELECT username FROM user WHERE username = (?)', (user,))
            username_check = c.fetchone()
            if not email_check and not username_check:
                return render_template('NEA_login.html', msg = 'Incorrect Username/Email or Password')
            c.execute('SELECT user_passSalt, user_passhash, user_id FROM user WHERE user_email = (?) OR username = (?)', (user, user))
            User_data = c.fetchall()
            user_passSalt = User_data[0][0]
            userpass_hash = User_data[0][1]
            user_id = User_data[0][2]
        for i in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
            if userpass_hash == SHA.SHA(passw + user_passSalt + i):
                session.permenant = True
                session["user_id"] = user_id
                BoolCategory = cateindbcheck(user_id)
                if not BoolCategory:
                    return  redirect('/welcome')
                else:
                    if not request.cookies.get('categories'):
                        categories = fetchcategoriesnweight(user_id)
                        resp = cookie(categories, '/homepage')
                        return resp
                    return redirect('/homepage')
        return render_template('NEA_login.html', msg = 'Incorrect Username/Email or Password')
    else:
        return render_template('NEA_login.html')

@webapp.route('/welcome', methods = ['POST', 'GET'])
def welcome():
    if "user_id" in session and not cateindbcheck(user_id := session.get('user_id')):
        if request.method =='POST':
            categories = request.form.getlist('cate')
            for i in range(len(categories)):
                categories[i] = categories[i][:-1]
            other_categories = list(set(list_of_cates)-set(categories))
            with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                user_id = session.get('user_id')
                for i in range(len(categories)):
                    c.execute('INSERT INTO subscribed_categories (user_id, category, category_weight) VALUES (?,?,?)', 
                    (user_id, cipher.encrypt(categories[i]), 10))
                for i in range(len(other_categories)):
                    c.execute('INSERT INTO subscribed_categories (user_id, category, category_weight) VALUES (?,?,?)', 
                    (user_id, cipher.encrypt(other_categories[i]), 1))
                c.execute('INSERT INTO user_activity (user_id, post_id) VALUES (?,?)', (user_id, ''))
            weightings = []
            for i in range(len(categories)):
                weightings.append(10)
            catenweight = []
            for x_i, y_i in zip(categories, weightings):
                catenweight.append(cipher.encrypt(x_i))
                catenweight.append(y_i)
            resp = make_response(redirect('/homepage'))
            resp.set_cookie('categories', json.dumps(catenweight), max_age=60*60*24*365)
            return resp
        else:
            return render_template('NEA_welcome.html', list = list_of_cates)
    elif "user_id" in session and not request.cookies.get('categories'):
        user_id = session.get('user_id')
        categories = fetchcategoriesnweight(user_id)
        resp = cookie(categories, '/homepage')
        return resp
    else:
        return redirect('/login')

@webapp.route('/homepage', methods = ['POST','GET'])
def homepage():
    if "user_id" not in session:
        return redirect('/login')
    elif not request.cookies.get('categories'):
        categories = fetchcategoriesnweight(session['user_id'])
        resp = cookie(categories, '/homepage')
        return resp
    elif request.method == 'POST': #when a search for post
        searchterm = request.form['searchterm'] #this retrieves the search term from the form
        searchterm = searchterm.replace(' ','-')
        return redirect('/search/'+searchterm)
    else:
        user_id = session["user_id"]
        with sql.connect(databaselocation) as conn:
            c = conn.cursor()
            c.execute('SELECT username FROM user WHERE user_id = (?)', (user_id,))
            username = c.fetchone()
        cates = request.cookies.get('categories')
        list_o_cates = json.loads(cates)
        posts = retrieve_posts_to_display(list_o_cates)
        return render_template('NEA_homepage.html', posts=posts, letter=(cipher.decrypt(username[0])[0]))

@webapp.route('/post/<id>/<sorted>', methods=['GET', 'POST'])#webapp route for displaying an individual post
def post(id, sorted):
    tags = fetchtags(id)
    user_id = session['user_id']
    if "user_id" not in session: #checks if a user is logged in
        return redirect('/login')
    elif request.method == 'POST': #when a comment is being made or post or comment is liked or post is saved for later
        specifer = request.form['instr']
        if specifer == 'upvotepost':
            with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                c.execute('SELECT post_id FROM liked_posts WHERE post_id = (?) AND user_id = (?)', (id, user_id))
                liked_check = c.fetchone()
                if liked_check:
                    return redirect('/post/'+id+'/'+sorted)
                c.execute('UPDATE posts SET post_likes=post_likes + 1 WHERE post_id = (?)', (id,))
                for i in tags:
                    c.execute('UPDATE subscribed_categories SET category_weight = category_weight + 6 WHERE user_id = (?) AND category = (?)', (user_id, i[0]))
                c.execute('INSERT INTO liked_posts (user_id, post_id) VALUES (?,?)', (user_id, id,))
        elif specifer == 'downvotepost':
            with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                c.execute('SELECT post_id FROM liked_posts WHERE post_id = (?) AND user_id = (?)', (id, user_id))
                liked_check = c.fetchone()
                if liked_check:
                    c.execute('DELETE FROM liked_posts WHERE post_id = (?) AND user_id = (?)', (id, user_id))
                c.execute('UPDATE posts SET post_likes=post_likes - 1 WHERE post_id = (?)', (id,))
                for i in tags:
                    c.execute('UPDATE subscribed_categories SET category_weight = category_weight - 2 WHERE user_id = (?) AND category = (?) AND category_weight>1', (user_id, i[0]))
                #decrease weighting of categories of post dont allow weighting to decrease past 1
        elif specifer == 'savelater':
            with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                c.execute('SELECT post_id FROM saved_for_later WHERE post_id = (?) AND user_id = (?)', (id, user_id))
                saved_check = c.fetchone()
                if saved_check:
                    return redirect('/post/'+id+'/'+sorted)
                c.execute('INSERT INTO saved_for_later (user_id, post_id) VALUES (?,?)', (user_id, id))
        elif specifer[-1]==' ': #comment is being made, however if the comment is upvotepost or something like or contains downvotecomment then the other if statements would be triggered
            specifer = specifer[:-1]
            with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                c.execute('INSERT INTO comments (comment_text, comment_likes, comment_date_created, user_id, post_id) VALUES (?,?,?,?,?)', (specifer, 0, date.today().strftime("%d/%m/%Y"), user_id, id))
        elif specifer.find('upvotecomment') == 0:
            with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                c.execute('UPDATE comments SET comment_likes=comment_likes + 1 WHERE comment_id = (?)', (specifer[13:],))
        elif specifer.find('downvotecomment')==0:
            with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                c.execute('UPDATE comments SET comment_likes=comment_likes - 1 WHERE comment_id = (?)', (specifer[15:],))
        elif specifer == 'clickedlink':
            with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                for i in tags:
                    c.execute('UPDATE subscribed_categories SET category_weight = category_weight + 10 WHERE user_id = (?) AND category = (?)', (user_id, i[0]))
        list_o_cates = fetchcategoriesnweight(session['user_id'])
        resp = cookie(list_o_cates, '/post/'+id+'/'+sorted)
        return resp
    else: #implement that if the link to the website is clicked then you increase the weight by a large amount and if a post is clicked on the homepage weight is increased again but by a smaller amount
        with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                for i in tags:
                    c.execute('UPDATE subscribed_categories SET category_weight = category_weight + 3 WHERE user_id = (?) AND category = (?)', (user_id, i[0]))
                c.execute('UPDATE user_activity SET post_id = (?) WHERE user_id = (?)', (id,user_id))
                c.execute('SELECT post_title, post_image_link, post_date_created, post_link, post_likes, post_type, post_text FROM posts WHERE post_id = (?)', (id,))
                post_data = c.fetchall()
                c.execute('SELECT comment_text, user_id, comment_likes, comment_date_created, comment_id FROM comments WHERE post_id =(?)', (id,))
                comments = c.fetchall()
                for i in range(len(comments)):
                    comments[i] = list(comments[i])
                    c.execute('SELECT username FROM user WHERE user_id = (?)', (comments[i][1],))
                    comments[i][1] = cipher.decrypt(c.fetchall()[0][0])
        if sorted =='true':
            comments = MergeSort(comments)
        comments = comments[::-1]
        return render_template('NEA_post.html', id=id, title = post_data[0][0], img = post_data[0][1], date_created = post_data[0][2],
        link = post_data[0][3], likes = post_data[0][4], type = post_data[0][5], text = post_data[0][6], comments = comments)

@webapp.route('/search/')
def emptysearch():
    return redirect('/homepage')

@webapp.route('/search/<search_term>', methods=['GET', 'POST'])
def search(search_term):
    if "user_id" not in session:
        return redirect('/login')
    elif not request.cookies.get('categories'):
        categories = fetchcategoriesnweight(user_id:=session.get('user_id'))
        resp = cookie(categories, '/homepage')
        return resp
    elif request.method == 'POST': #when a search for post
        searchterm = request.form['searchterm'] #this retrieves the search term from the form
        searchterm = searchterm.replace(' ','-')
        return redirect('/search/'+searchterm)
    else:
        user_id = session["user_id"]
        with sql.connect(databaselocation) as conn:
            c = conn.cursor()
            c.execute('SELECT username FROM user WHERE user_id = (?)', (user_id,))
            username = c.fetchone()
        search_term = search_term.replace('-',' ')
        if search_term in list_of_cates:
            posts = retrieve_tagged_posts(search_term)
        else:
            posts = retrieve_search_results(search_term)
        return render_template('NEA_homepage.html', posts=posts,  letter = cipher.decrypt(username[0])[0])

@webapp.route('/account/<id>', methods = ['GET', 'POST'])
def accountposts(id):
    id = id.replace(' ','')
    if "user_id" not in session: return redirect('/login')
    elif request.method == 'POST':
        remove_post_id = request.form['instr']
        with sql.connect(databaselocation) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM saved_for_later WHERE post_id = (?) AND user_id = (?)', (remove_post_id, session['user_id']))
        return redirect('/account/'+id)
    elif id == 'saved_for_later' or id == 'liked_posts':
        if id == 'saved_for_later':
            title = 'Saved posts'
            with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                c.execute('SELECT post_id FROM saved_for_later WHERE user_id = (?)', (session['user_id'],))
                posts = retrieve_posts(c.fetchall())
        elif id == 'liked_posts':
            with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                c.execute('SELECT post_id FROM liked_posts WHERE user_id = (?)', (session['user_id'],))
                posts = retrieve_posts(c.fetchall())
            title = 'Liked posts'
        return render_template('NEA_accountposts.html', title = title, posts = posts)
    else:
        return redirect('/account')

@webapp.route('/account', methods = ['GET'])
def accountpage():
    return render_template('NEA_account.html')

@webapp.route('/account/', methods = ['GET'])
def emptyaccountpage():
    return redirect('/account')

@webapp.route('/friendactivity', methods = ['GET', 'POST'])
def friendactivity():
    if 'user_id' not in session: return redirect('/login')
    elif request.method == 'POST':
        user_id = session.get('user_id')
        instruction = request.form['instr']
        if instruction[-1] == ' ': # searching a username
            username = instruction[:-1]
            users = retrieve_user_search(username)
            posts = retrieve_friends_posts(user_id)
            requests = retrieve_requests(user_id)
            return render_template('NEA_friendactivity.html', posts=posts, requests=requests, search=users)
        elif instruction[:7] == 'Request':
            reqeusted_user = instruction[11:]
            if reqeusted_user == user_id: return redirect('/friendactivity')
            with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                c.execute('SELECT user_id FROM friends WHERE user_id = (?) AND friend_id = (?)', (user_id, reqeusted_user))
                alrdyfriends = c.fetchall()
                c.execute('SELECT user_id FROM friendship_reqs WHERE user_id = (?) AND requesting_user_id = (?)', (reqeusted_user, user_id))
                if not c.fetchall() and not alrdyfriends:
                    c.execute('INSERT INTO friendship_reqs (user_id, requesting_user_id) VALUES (?,?)', (reqeusted_user, user_id))
            return redirect('/friendactivity')
        elif instruction[:3]=='Add':
            addinguser = instruction[7:]
            if addinguser == user_id: return redirect('/friendactivity')
            with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                c.execute('INSERT INTO friends (user_id, friend_id) VALUES (?,?)',(user_id, addinguser))
                c.execute('INSERT INTO friends (user_id, friend_id) VALUES (?,?)',(addinguser, user_id))
                c.execute('DELETE FROM friendship_reqs WHERE requesting_user_id = (?) AND user_id = (?)',(addinguser, user_id))
            return redirect('/friendactivity')
        elif instruction[:6]=='Ignore':
            ignoreuser = instruction[10:]
            with sql.connect(databaselocation) as conn:
                c = conn.cursor()
                c.execute('DELETE FROM friendship_reqs WHERE requesting_user_id = (?) AND user_id = (?)',(ignoreuser, user_id,))
            return redirect('/friendactivity')
    else:
        user_id = session.get('user_id')
        requests = retrieve_requests(user_id)
        posts = retrieve_friends_posts(user_id)
        return render_template('NEA_friendactivity.html', posts = posts, requests=requests, search=[])#pass username and userid

@webapp.route('/logout')
def logout():
    session.clear()
    res = make_response(redirect('/login'))
    res.set_cookie('categories', '', expires=0)
    return res

@webapp.route('/linkclicked')
def return_some_data():
    post_id = request.referrer[-8:]
    tags = fetchtags(post_id)
    with sql.connect(databaselocation) as conn:
        c = conn.cursor()
        for i in tags:
            c.execute('UPDATE subscribed_categories SET category_weight = category_weight + 6 WHERE user_id = (?) AND category = (?)', (session['user_id'], cipher.encrypt(i[0])))
    return '', 204


def saltandpeppergenerator():
    slen = 10
    salt_list = rand.choices(range(33, 127), k = slen) #ascii numbers for all letters including capital,
    salt=''                                            # numbers and special characters
    for i in salt_list:
        salt += chr(i)
    pepper = rand.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', k = 1) #here I manually
    return salt, pepper[0]          #input the entire alphabet with capital as they are not adjacent in ascii

def cateindbcheck(user_id):
    with sql.connect(databaselocation) as conn:
        c = conn.cursor()
        c.execute('SELECT category FROM subscribed_categories WHERE user_id = (?)', (str(user_id),))
        BoolCategory = c.fetchone()
    return bool(BoolCategory)

def fetchcategoriesnweight(user_id):
    with sql.connect(databaselocation) as conn:
        c = conn.cursor()
        c.execute('SELECT category, category_weight FROM subscribed_categories WHERE user_id = (?)', (str(user_id),))
        categories = c.fetchall()
        return categories

def cookie(categories, address):
    cate = []
    for i in range(len(categories)):
        cate.append(categories[i][0])
        cate.append(categories[i][1])
    res = make_response(redirect(address))
    res.set_cookie('categories', json.dumps(cate), max_age=60*60*24*365) #https://stackoverflow.com/questions/58966233/flask-set-cookies-using-list
    return res

def generate_id(type):
    id = ''.join(rand.choices('0123456789abcdef', k =8))
    with sql.connect(databaselocation) as conn:
        c = conn.cursor()
        if type == 'user':
            c.execute('SELECT user_id FROM user WHERE user_id = (?)', (id,))
            user_id_exists = c.fetchone()
            if user_id_exists:
                id = generate_id('user')
        elif type == 'post':
            c.execute('SELECT post_id FROM posts WHERE post_id = (?)', (id,))
            post_id_exists = c.fetchone()
            if post_id_exists:
                id = generate_id('post')
    return id

def retrieve_friends_posts(user_id):
    posts = []
    friendsusernames = []
    with sql.connect(databaselocation) as conn:
        c = conn.cursor()
        c.execute('SELECT friend_id FROM friends WHERE user_id = (?)', (user_id,))
        friends = c.fetchall()
        for friend_id in friends:
            c.execute('SELECT username FROM user WHERE user_id = (?)', (friend_id[0],))
            friendsusernames.append(cipher.decrypt(c.fetchall()[0][0]))
        for i in friends:
            c.execute('SELECT post_id FROM user_activity WHERE user_id = (?)', (i[0],))
            foo = c.fetchall()
            if foo[0]:
                posts+=foo
        posts = retrieve_posts(posts)
        posts_to_display = []
        for i in range(len(posts)):
            if posts[i]:
                posts[i]+=(friendsusernames[i],)
                posts_to_display.append(posts[i])
    return posts_to_display

def retrieve_requests(user_id):
    with sql.connect(databaselocation) as conn:
        c = conn.cursor()
        c.execute('SELECT requesting_user_id FROM friendship_reqs WHERE user_id = (?)', (user_id,))
        requests = c.fetchall()
        users = []
        for i in requests:
            c.execute('SELECT user_id, username FROM user WHERE user_id = (?)', (i[0],))
            users+=c.fetchall()
        users = [list(user) for user in users]
        for i in range(len(users)):
            users[i][1] = cipher.decrypt(users[i][1])
    return users

def retrieve_posts_to_display(list):
    no_of_posts = 36
    categories = []
    weights = []
    posts_per_category = []
    post_ids = []
    for i in range(len(list)):
        if i%2 == 0:
            categories.append(cipher.decrypt(list[i]))
        else:
            weights.append(list[i])
    total = sum(weights)
    for i in range(len(weights)):
        posts_per_category.append(int((weights[i]/total)*no_of_posts))
    with sql.connect(databaselocation) as conn:
            c = conn.cursor()
            for category, number in zip(categories, posts_per_category):
                c.execute('SELECT post_id FROM post_tags WHERE post_tag = (?) ORDER BY random() LIMIT (?)', (category, number))
                post_ids.extend(c.fetchall())
    posts = retrieve_posts(post_ids)
    return posts

def retrieve_user_search(searchterm):
    users = []
    searchterm = cipher.encrypt(searchterm)
    with sql.connect(databaselocation) as conn:
        c = conn.cursor()
        for i in range(len(searchterm)):
            c.execute('SELECT user_id, username FROM user WHERE username LIKE (?) LIMIT 10', (searchterm[:(-1+i*-1)]+'%',))
            users += c.fetchall()
        users = list(dict.fromkeys(users))
        users = [list(user) for user in users]
        for i in range(len(users)):
            users[i][1] = cipher.decrypt(users[i][1])
    return users

def retrieve_search_results(searchterm):
    searchterm = '%'+searchterm+'%'
    with sql.connect(databaselocation) as conn:
        c = conn.cursor()
        c.execute('SELECT post_title, post_image_link, post_likes, post_type, post_id FROM posts WHERE post_title LIKE (?) LIMIT 36', (searchterm,))
        posts = c.fetchall()
        for i in range(len(posts)):
            tags = ''
            c.execute('SELECT post_tag FROM post_tags WHERE post_id = (?)', (posts[i][4],))
            list_tags = c.fetchall()
            for tag in list_tags:
                tags+=tag[0]+' '
            posts[i]+=(tags,)
    return posts

def retrieve_tagged_posts(category):
    with sql.connect(databaselocation) as conn:
        c = conn.cursor()
        c.execute('SELECT post_id FROM post_tags WHERE post_tag = (?) ORDER BY random() LIMIT 36', (category,))
        posts = retrieve_posts(c.fetchall())
    return posts

def retrieve_posts(post_ids):
    posts = []
    for i in post_ids:
        with sql.connect(databaselocation) as conn:
            c = conn.cursor()
            c.execute('SELECT post_title, post_image_link, post_likes, post_type, post_id FROM posts WHERE post_id = (?)', (i[0],))
            post = c.fetchone()
            posts.append(post)
    for i in range(len(posts)):
        tags = ''
        if posts[i]:
            c.execute('SELECT post_tag FROM post_tags where post_id = (?)', (posts[i][4],))
            list_tags = c.fetchall()
            for tag in list_tags:
                tags+=tag[0]+' '
            posts[i]+=(tags,)
    return posts

def fetchtags(post_id):
    with sql.connect(databaselocation) as conn:
        c = conn.cursor()
        c.execute('SELECT post_tag FROM post_tags where post_id = (?)', (post_id,))
        list_tags = c.fetchall()
    #print(list_tags)
    return list_tags


if __name__ == '__main__':
    webapp.run(debug = True)
