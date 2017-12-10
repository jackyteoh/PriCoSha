from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                       port=8889,
                       user='root',
                       password='root',
                       db='PriCoSha',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
@app.route('/')
def hello():
	return render_template('index.html')

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/confirm')
def confirm():
	return render_template('confirm.html')

@app.route('/post')
def postpage():
	return render_template('post.html')

@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():

	username = request.form['username']
	password = request.form['password']
	cursor = conn.cursor()
	query = 'SELECT * FROM Person WHERE username = %s and password = %s'
	cursor.execute(query, (username,password))
	data = cursor.fetchone()
	cursor.close()
	error = None
	if(data):
		session['username'] = username
		return redirect(url_for('home'))
	else:
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	
	username = request.form['username']
	password = request.form['password']
	firstname = request.form['fname']
	lastname = request.form['lname']
	cursor = conn.cursor()
	query = 'SELECT * FROM Person WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	error = None
	if(data):
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO Person VALUES(%s, %s, %s, %s)'
		cursor.execute(ins, (username, password,firstname,lastname))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/home')
def home():
    username = session['username']
    sql ="select id, content_name from Content  where id in (select distinct(id) from content  where public = true or id in (select DISTINCT(id) from Member join Share using(group_name) where Member.username = %s)) order by timest DESC"
    cursor = conn.cursor()
    cursor.execute(sql,(username))
    #data = cursor.fetchall()
    data = cursor.fetchall()

    cursor2 = conn.cursor()
    sql2 = 'Select id,username,comment_text from  Comment where id in (select distinct(id) from content   where public = true or id in (select DISTINCT(id) from Member join Share using(group_name) where Member.username = %s) )'
    cursor2.execute(sql2, (username))
    data2 = cursor2.fetchall()

    cursor3 = conn.cursor()
    sql3 = 'select id, first_name,last_name from((select distinct(id), first_name,last_name from content natural join Person where public = true or id in (select DISTINCT(id) from Member join Share using(group_name) where Member.username = %s)) as sub  natural join tag) where status = "1"'
    cursor3.execute(sql3, (username))
    data3 = cursor3.fetchall()

    cursor4 = conn.cursor()
    sql4 = """select id, first_name,last_name,username_tagger from((select distinct(id), first_name,last_name from content natural join Person where public = true or id in (select DISTINCT(id) from Member join Share using(group_name) where Member.username = %s)) as sub  natural join tag) where status="0" and username_taggee = %s"""
#     sql4 = """select id, first_name,last_name,username_tagger
# from((select distinct(id), first_name,last_name
# from content natural join Person
# where public = true or id in
#     		(select DISTINCT(id)
# 				from Member join Share using(group_name)
# 				where Member.username = %s)) as sub  natural join tag) where status="0" and username_taggee = %s """
    cursor4.execute(sql4, (username, username))
    data4 = cursor4.fetchall()


    return render_template('home.html', username=username, data=data, data2=data2,data3=data3, data4 = data4)

@app.route('/postform', methods=['GET', 'POST'])
def post():
    title = request.form['title']
    username = session['username']
    state = request.form['privacy']
    cursor = conn.cursor()
    query = 'INSERT INTO Content(username,content_name,public) VALUES(%s, %s,%s)'
    cursor.execute(query, (username, title, state))
    conn.commit()
    cursor.close()
    if state == "0":
        cursor = conn.cursor()
        query = 'Select group_name From FriendGroup where username = %s'
        cursor.execute(query, username)
        data = cursor.fetchall()
        if(data):
            return render_template('post.html', data=data)
        else:
            error = "This User Doesn't own any FriendGroup"
            return render_template('register.html', error=error)
    else:
        msg = 'You have made a new public post!!'
        return render_template('post.html', msg=msg)

@app.route('/selectgroup', methods=['GET', 'POST'])
def selectgroup():
    multiselect = request.form.getlist('mymultiselect')
    cursor = conn.cursor()
    query = 'Select max(id) From Content'
    cursor.execute(query)
    data = cursor.fetchone()
    data2 = data[u'max(id)']

    username = session['username']
    query = 'INSERT INTO Share VALUES(%s, %s,%s)'
    for group in multiselect:
        cursor = conn.cursor()
        cursor.execute(query, (data2, group, username))
        conn.commit()
        cursor.close()
    return render_template('post.html')

@app.route('/tagconfirm', methods=['GET', 'POST'])
def tagconfirm():
    state = request.form['status']
    cid = request.form['id']
    username = session['username']
    tagger = request.form['tagger']
    cursor = conn.cursor()
    cursor2 = conn.cursor()

    if state == "1":
        query = "update Tag set status = 1 where id = %s"
        cursor.execute(query, cid)
        conn.commit()
        cursor.close()

    if state == "-1":
        query2 = 'Delete from Tag where id = %s and username_taggee = %s and username_tagger = %s'
        cursor2.execute(query2, (cid, username, tagger))
        conn.commit()
        cursor2.close()

    # if state == 1:
    #     return redirect(url_for('login.html'))
    # if state == -1:
    #     return redirect(url_for('post.html'))

    return render_template('confirm.html')

@app.route('/addFriend')
def addFriend():
  friendGroup = request.form['Friend Group']
  cursor = conn.cursor()
  query = 'SELECT * FROM friendgroup WHERE friendGroup = %s'
  cursor.execute(query, (friendGroup))
  data = cursor.fetchone()
  error = None
  
  firstname = request.form['f_name']
  lastname = request.form['l_name']
  cursor2 = conn.cursor2()
  query2 = 'SELECT * FROM Person WHERE firstname = %s AND lastname = %s'
  cursor2.execute(query, (firstname, lastname))
  data2 = cursor2.fetchone()
  error2 = None
  if (data): #Error of friendGroup not existing
    error = "This friendGroup does not exist."
    return render_template('addFriend.html', error = error)
  else:
  	if (data2): #Error of person that you are trying to add does not exist
    	error2 = "This person does not exist."
    	return render_template('addFriend.html', error2 = error2)
  	else if (data2): #Error of person already existing in the friendGroup
    	error2 = "This person is already in this friend group."
    	return render_template('addFriend.html', error2 = error2)
  	else if (data2): #Error of multiple people having the same name
    	error2 = "There are multiple people with this name. Please give their username."
    	username = request.form['username']
    	cursor3 = conn.cursor3()
    	query3 = 'SELECT * FROM Person WHERE firstname = %s AND lastname = %s AND username = %s'
    	cursor3.execute(query, (firstname, lastname, username))
    	data3 = cursor3.fetchone()
    	error3 = None
    	if (data3): #Error of the firstname, lastname, and username combo not existing
      	error3 = "This firstname, lastname, and username combo does not exist."
      	return render_template('addFriend.html', error3 = error3)
    	else:
      	ins = 'INSERT INTO friendGroup VALUES (%s, %s, %s)
      	cursor.execute(ins, (firstname, lastname, username))
        #Need to also add the friendGroup into the added person's friendGroup
        #ins2 = 'INSERT INTO friendGroup VALUES (%s)
        #cursor3.execute(ins2, (friendGroup))
        #data3.execute(ins2, (friendGroup))     NOT SURE WHICH ONE TO USE HERE cursor3 or data3
        
        #Need to also add into Member table
      	#ins3 = 'INSERT INTO member VALUES (%s, %s, %s)
      	#cursor3.execute(ins3, (username, groupname, group_creator))
      	#data3.execute(ins3, (username, groupname, group_creator))
      	#username would be the username of the person being added, already given here.
      	#groupname would be name of the friendGroup that they are being added to.
      	#group_creator would be the username of the person owning/created the friendGroup, query by using the friendGroup name to find the username of the creator?
      
        #cursor3.close()
        #Do i need cursor2.close() ?
        
      	conn.commit()
      	cursor.close()
      	return render_template('addFriend.html')
  	else if (data2):
    	ins = 'INSERT INTO friendGroup VALUES (%s, %s)'
    	cursor.execute(ins, (firstname, lastname))
      #Need to also add the friendGroup into the added person's friendGroup
      #ins2 = 'INSERT INTO friendGroup VALUES (%s)
      #cursor3.execute(ins2, (friendGroup))
      #data3.execute(ins2, (friendGroup))     NOT SURE WHICH ONE TO USE HERE cursor3 or data3
      
      #Need to also add into Member table
      #ins3 = 'INSERT INTO member VALUES (%s, %s, %s)
      #cursor3.execute(ins3, (username, groupname, group_creator))
      #data3.execute(ins3, (username, groupname, group_creator))
      #username would be the username of the person being added, query for that?
      #groupname would be name of the friendGroup that they are being added to.
      #group_creator would be the username of the person owning/created the friendGroup, query by using the friendGroup name to find the username of the creator?
      #cursor3.close()
      #Do i need cursor2.close() ?
      
    	conn.commit()
    	cursor.close()
    	return render_template('addFriend.html')
  
@app.route('/manageTags')
def manageTags():
  #Already needs to be in the session, not sure how to put this in code
  #Write a query to see all the possible tags? 'SELECT * FROM tag WHERE ???'
  #Have the html functions in manageTags.html allow the user to check off certain tags they select
  #Have 3 HTML functions, "Accept", "Decline", "Remove", "Return" (Maybe add another 2, Select All & Deselect All ?)
  #Accept changes the tag status to "True"
  #When we change it to true do we need to go to each content item and have the tag there?
  #Decline removes the tag from the tag table of both parties
  #Remove changes the tag status to "False"
  #When we change it to false do we need to go to each content item and remove the tag from there?
  #Accept/Decline needs to change the status on the tagger's tag table as well?
  #Return returns the user back to the home page with other options

@app.route('/comment')
def comment():
  #Already needs to be in the session, not sure how to put this in code
  #query = 'SELECT * FROM content WHERE ???'
  #Have html functions like the manageTags function, with multiple buttons: Comment, Like, Unlike
  #Combining two functions into one
  #Allow the user to select one only? And press Comment button allows them to write the comment they desire
  #comment = request_form['Comment here']
  #Take the ID from the content selected/checked off (not sure how to implement this)
  #
  
@app.route('/like)
def like():
  #Already needs to be in the session, not sure how to put this in code         
@app.route('defriend')
def defriend():
  #Already needs to be in the session, not sure how to put this in code
app.secret_key = 'some key that you will never guess'
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
