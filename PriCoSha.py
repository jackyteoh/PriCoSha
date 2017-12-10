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
	return render_template('home.html', username=username)

@app.route('/postform', methods=['GET', 'POST'])
def post():
    title = request.form['title']
    username = session['username']
    privacy = request.form['privacy']
    cursor = conn.cursor()
    query = 'INSERT INTO Content (username,content_name,public) VALUES(%s, %s,%s)'
    cursor.execute(query, (username, title, privacy))
    conn.commit()
    cursor.close()
    if privacy == "false":
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
    last = 'LAST_INSERT_ID()'
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
        
app.secret_key = 'some key that you will never guess'
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
