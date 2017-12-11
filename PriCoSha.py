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

@app.route('/addFriend', methods=['GET', 'POST'])
def addFriend():
  friendGroup = request.form['Friend Group']
  master_username = session['username']
  cursor = conn.cursor()
  query = 'SELECT * FROM friendgroup WHERE group_name = %s'
  groupname = 'SELECT group_name FROM friendgroup WHERE group_name = %s'
  cursor.execute(query, (friendGroup))
  data = cursor.fetchone()
  error = None
  
  firstname = request.form['f_name']
  lastname = request.form['l_name']
  cursor2 = conn.cursor2()
  cursor4 = conn.cursor4()
  query2 = 'SELECT * FROM Person WHERE firstname = %s AND lastname = %s'
  query4 = 'SELECT COUNT(*) FROM Person WHERE firstname = %s AND lastname = %s'
  cursor2.execute(query2, (firstname, lastname))
  cursor4.execute(query4, (firstname, lastname))
  data2 = cursor2.fetchall()
  data4 = cursor4.fetchone()
  error2 = None
  if (!data): #Error of friendGroup not existing
    error = "This friendGroup does not exist."
    return render_template('addFriend.html', error = error)
  else:
  	if (!data2): #Error of person that you are trying to add does not exist
    	error2 = "This person does not exist."
    	return render_template('addFriend.html', error2 = error2)
  	else if (data2): #Error of person already existing in the friendGroup
      #Need to change this, check member group to see if they're inside it already
      #check for username
      query5 = 'SELECT username FROM member WHERE username = (SELECT username FROM Person WHERE first_name = firstname AND last_name = lastname)'
      cursor5.execute(query5, (firstname, lastname))
      data5 = cursor5.fetchone()
      error5 = none
      if (data5):
        error5 = "This person already exists inside the friend group! Or are you trying to add a different user with the same name?"
      	username = request.form['username']
        if (data5 = username):
          error6 = "This is the same person!!!!"
        	return render_template('addFriend.html', error6 = error6)
      	else:
          query7 = 'INSERT INTO member VALUES (%s, %s, %s)'
          cursor.execute(query7, (username, groupname, master_username))
          conn.commit()
          cursor.close()
    			return render_template('addFriend.html')
  	else if (data2 and data4 > 1): #Error of multiple people having the same name
    	error2 = "There are multiple people with this name. Please give their username."
    	username = request.form['username']
    	cursor3 = conn.cursor3()
    	query3 = 'SELECT * FROM Person WHERE firstname = %s AND lastname = %s AND username = %s'
    	cursor3.execute(query, (firstname, lastname, username))
    	data3 = cursor3.fetchone()
    	error3 = None
    	if (!data3): #Error of the firstname, lastname, and username combo not existing
      	error3 = "This firstname, lastname, and username combo does not exist."
      	return render_template('addFriend.html', error3 = error3)
    	else:
      	ins = 'INSERT INTO member VALUES (%s, %s, %s)'
      	cursor.execute(ins, (username, groupname, master_username))
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
    	ins = 'INSERT INTO member VALUES (%s, %s, %s)'
      username2 = 'SELECT username FROM Person WHERE first_name = firstname AND last_name = lastname'
    	cursor.execute(ins, (username2, groupname, master_username))
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
  
@app.route('/manageTags', methods=['GET', 'POST'])
def manageTags():
  #Already needs to be in the session, not sure how to put this in code
  username = session['username']
  #Write a query to see all the possible tags? 'SELECT * FROM tag WHERE ???'
  query = 'SELECT * FROM tag WHERE username_tagger = username OR username_taggee = username'
  cursor = conn.cursor()
  cursor.execute(query, (username))
  data = cursor.fetchone()
  #data = cursor.fetchall()
  error = None
  
  #Have the html functions in manageTags.html allow the user to check off certain tags they select
  #Have 3 HTML functions, "Accept", "Decline", "Remove", "Return" (Maybe add another 2, Select All & Deselect All ?)
  #Accept changes the tag status to "True"
  accept = 'UPDATE tag SET status = "True" WHERE selected.id = tag.id AND username_taggee = username'
  #Below problem, how do we update the tag table of the tagger to true? What conditions do we need?
  accept2 = 'UPDATE tag SET status = "True" WHERE selected.id = tag.id AND username_tagger = '
  #Decline removes the tag from the tag table of both parties
  decline = 'DELETE FROM tag WHERE selected.id = tag.id AND username_taggee = username'
  #Same problem as with accept, how do we delete this tag from the tagger's tag table?
  decline2 = 'DELETE FROM tag WHERE selected.id = tag.id AND username_tagger = '
  #Remove changes the tag status to "False"
  remove = 'UPDATE tag SET status = "False" WHERE selected.id = tag.id AND username_taggee = username'
  #Same problem as above.
  remove2 = 'UPDATE tag SET status = "False" WHERE selected.id = tag.id AND username_tagger = '
  #Accept/Decline needs to change the status on the tagger's tag table as well?
  #Return returns the user back to the home page with other options
  conn.commit()
  cursor.close()
  return render_template('managetags.html')

@app.route('/comment', methods=['GET', 'POST'])
def comment():
  #Already needs to be in the session, not sure how to put this in code
  #query = 'SELECT * FROM content WHERE ???'
  #Have html functions like the manageTags function, with multiple buttons: Comment, Like, Unlike
  #Combining two functions into one
  #Allow the user to select one only? And press Comment button allows them to write the comment they desire
  #comment = request_form['Comment here']
  #['Comment'] button HTML
  #Take the ID from the content selected/checked off (not sure how to implement this)
  #id = 'SELECT ID FROM content WHERE selected = "TRUE"' ?
  #username = session['username'] <-- pull the username from the current session?
  #How do we get the current timestamp? Is there a python function to get the current time?
  #time = 
  #Once ['Comment'] button is pressed, run the below query.
  #query2 = 'INSERT INTO comment VALUES (id, username, time, comment)'
  #after this return to the viewcontent page? the comment page? at viewcontent you can view the content/comment/like/unlike ?
  return render_template('comment.html')
	return render_template('viewcontent.html')

@app.route('/like', methods=['GET', 'POST'])
def like():
  #Already needs to be in the session, not sure how to put this in code         
  #query = 'SELECT * FROM content WHERE ???'
  #Use HTML functions from above^
  #Maybe add another column to the content table? "Likes" initialized to 0 with every post
  #id = 'SELECT id from content WHERE selected = 'TRUE'' ? <-- how do we mark this?
  #Then do we need to show who liked it? Or just the number of likes?
  #If we keep track of who liked it, maybe we need another table in content? Likers?
  #Are there vectors in python? Or does this even work in mySQL ? Can we have a list of likers inside a mySQL table?
  #If we keep track of just the number of likes:
  #likes = 'SELECT likes FROM content WHERE content.id = selected.id ? WHERE selected = TRUE ?'
  #Above query not needed if likes = likes + 1 / likes++ / likes+= 1 works
  #like = 'UPDATE content SET likes = likes + 1 ? likes++ ? likes+=1 ? WHERE content.id = SELECTED.id?' if ['Like'] button is pressed
  #If we do unlike, we can just use the same query but subtract 1 instead.
  #unlike = 'UPDATE content SET likes = likes - 1 ? likes-- ? likes-= 1? WHERE content.id = SELECTED.id' if ['Unlike'] button is pressed.
  #Not sure how to denote which one to update (in the WHERE clause) how do we keep track of which ID got selected? Do we store that in a different variable? (ln 296)
  #If we keep track of the actual likers:
  #Like: if they like the content, add their username to the vector (?) of usernames in the content. not sure how to implement this. maybe counting likes is easier
  #Unlike: if they unlike it, remove their username from the vector of usernames in the content
  #Maybe don't keep track of the likers ? Could be easy to implement, have a view likes button. returns table of the user ids who liked it + like count
  #Not sure how they're going to be stored though thats the main issue
  return render_template('like.html')
  return render_template('viewcontent.html')
           
@app.route('defriend', methods=['GET', 'POST'])
def defriend():
  
  cursor = conn.cursor()
  error = None
  #Already needs to be in the session, not sure how to put this in code
  #Need to see a list of the friends of the session user? add friendslist column to Person table?
  #Same issue with how we store a friendslist. vector in mySQL ?
  #Maybe make another table itself called friendslist? Store by username/ID and friendid/friendusername ?
  #Size would be huge. Twice the number of friendships (friendships are mutual)
  #username = session['username']
  #query = 'SELECT friendslist FROM person WHERE username = username'
  #Have the HTML function from above functions, except be able to select multiple for this one. Have select all/deselect all too (?)
  #[Unfriend] button
  #If [Unfriend] button is pressed:
  #Remove them from each other's friendslist if we implement this
  #Remove the unfriended person from members of any friendGroup owned by the unfriender:
  #username2 = 'SELECT username FROM friendslist WHERE selected = "TRUE"' ?
  #unfriender = 'DELETE FROM username.friendslist WHERE username = username2'
	#unfriendee = 'DELETE FROM username2.friendslist WHERE username = username'
  #unfriendeegroup = 'DELETE FROM username2.member WHERE username_creator = username'
  #I don't think anything needs to be done on the friend group owner side. Just needs to delete them from being a member of the friendgroup.
  #unfriendeecontent = 'DELETE FROM username2.content WHERE username = username' deletes any content shared by the unfriender
  #I believe we can still leave comments on content, they usually stay on other platforms even if you unfriend someone
  #unfriendeetag = 'DELETE FROM username2.tag WHERE (username_tagger = username AND username_taggee = username2) OR (username_tagger = username2 AND username_taggee = username)
	#unfriendertag = 'DELETE FROM username.tag WHERE (username_tagger = username AND username_taggee = username2) OR (username_tagger = username2 AND username_taggee = username)
  #I think this covers all the possible problems that could occur with unfriending someone, we can use these in the summary/write this in full sentences.
  conn.commit()
  cursor.close()
  return render_template('friendslist.html') #If we have an html for friendslist, what options would it have besides unfriending ?
  return render_template('defriend.html')
           
app.secret_key = 'some key that you will never guess'
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
-
