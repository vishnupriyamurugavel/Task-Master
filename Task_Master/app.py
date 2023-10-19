from flask import Flask,render_template,url_for,redirect,request,session,Response
from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3 as sql
import logging

app=Flask(__name__) 
app.config.from_pyfile('config.py', silent=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 
handler = logging.FileHandler('todo.log')
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')) 
logger.addHandler(handler) 

def updatequery(query, values):
    ''' Executes the create, update and delete SQL queries. '''
    try:
        connection = sql.connect('Database.db')
        cursor = connection.cursor()
        cursor.execute(query, values)
        connection.commit()
        logger.info(f'Executed SQL query: {query} with values: {values}')
    except sql.Error as e:
        # if an error occurs, roll back the changes and log the error
        connection.rollback()
        logger.error(f'Error executing SQL query: {query} with values: {values}. Error message: {str(e)}')
    finally:
        if connection:
            connection.close()

def selectquery(query, values):
    ''' Executes the select SQL query and returns the result. '''
    try:
        connection = sql.connect('Database.db')
        cursor = connection.cursor()
        cursor.execute(query, values)
        data = cursor.fetchall()
        logger.info(f'Executed SQL query: {query} with values: {values}')
        return data

    except sql.Error as e:
        # if an error occurs, log the error
        logger.error(f'Error executing SQL query: {query} with values: {values}. Error message: {str(e)}')
        return None

    finally:
        if connection:
            connection.close()

# ..........................Creates users, lists and tasks table if not exists.....................................
updatequery("create table if not exists users(user_id integer primary key autoincrement,username text, email text not null, password text not null)",())
updatequery("create table if not exists lists(list_id integer primary key autoincrement,list_name text,username text)",())
updatequery("create table if not exists todo (task_id integer primary key autoincrement ,username text,title text,list text, createddate text,duedate text,status integer)",())


@app.route("/")
def main():
    return redirect(url_for('login'))

#..........................USER AUTHENTICATION FUNCTIONS.........................................
@app.route("/login",methods=('GET','POST'))
def login():
    ''' Renders login page and redirects the user to the tasks page upon successful login. '''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  
        data = selectquery('SELECT password FROM users WHERE username = ?', [username])

        if data:         
            hashed_password = data[0][0]
            if check_password_hash(hashed_password, password):    
                # log successful login
                logger.info(f'User {username} logged in successfully.')
                session['list'] = 'All lists'
                session['username'] = username 
                return redirect(url_for("tasks")) 

            else:
                message = "Invalid Password"
                logger.warning(f'User {username} entered an invalid password during login.')
                return render_template("login.html",message=message) 

        else:
            message = "Invalid username/ User not exits"
            logger.warning(f'User {username} entered an invalid username during login.')
            return render_template("login.html",message=message)

    return render_template("login.html")

@app.route("/register",methods=('GET','POST'))
def register():
    '''Renders registration page and registration only proceeds if the entered username 
        and email do not match existing data.'''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # check if the username already exists in the database
        if selectquery("SELECT * FROM users WHERE username = ?", [username]):
            logger.warning(f'User attempted to register with an existing username: {username}')
            return render_template('register.html', message='Username already exists')

        # check if the email already exists in the database
        if selectquery("SELECT * FROM users WHERE email = ?", [email]):
            logger.warning(f'User attempted to register with an existing email: {email}')
            return render_template('register.html', message='Email already exists')        

        # hash the password and add the user to the database
        password = generate_password_hash(password) 
        updatequery('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))   
        updatequery('INSERT INTO lists (list_name, username) VALUES (?, ?)', ('Default', username))     
        session['username'] = username         
        session['list'] = 'All lists'
        
        # log successful registration
        logger.info(f'New user registered successfully: {username}')

        return redirect(url_for('tasks'))

    return render_template('register.html')

#............................................TASKS PAGE................................................................

@app.route("/tasks",methods=('GET','POST'))
def tasks():
    ''' Returns tasks in a particular list if mentioned else returns all the tasks.'''
    logger.info("Tasks route requested.")
    import datetime
    today = datetime.date.today()
    today=today.strftime("%Y-%m-%d") 
    updatequery("update todo set status=-1 where status=0 and duedate<'"+today+"'",())
    updatequery("update todo set status=0 where status=-1 and duedate>'"+today+"'",())
    if request.method=='POST':
        logger.debug("Handling POST request.")
        search=request.form['search']
        search="%"+search+"%"
        tasks=selectquery("select * from todo where username = ? and (title like ? or duedate like ? or list like ?)",(session['username'],search,search,search))
        lists=selectquery('select * from lists where username=?',[session['username']])
        return render_template("searchtask.html",tasks=tasks,lists=lists)
    else:
        logger.debug("Handling GET request.")
        if session['list']=='All lists':
            tasks=selectquery('select * from todo where username = ?',[session['username']])
        else:
            tasks=selectquery('select * from todo where username = ? and list=?',(session['username'],session['list'])) 
        lists=selectquery('select * from lists where username=?',[session['username']])

        logger.debug(f"List name: {session['list']}")
        logger.debug(f"Tasks found: {len(tasks)}")

        return render_template("tasks.html",tasks=tasks,lists=lists)

@app.route("/add_task",methods=('GET','POST'))
def add_task():
    if request.method=='POST':
        from datetime import datetime
        now = datetime.now()
        createddate= now.strftime("%Y-%m-%d %H:%M:%S")
        username=session['username']
        title= request.form['title']
        list=request.form['list']
        duedate=request.form['duedate'] 
        status=0
        updatequery('insert into todo(username,title,list,createddate,duedate,status) values(?,?,?,?,?,?)',(username,title,list,createddate,duedate,status))
        logging.info('New task added by user: %s', username) # log the addition of new task
        return redirect(url_for("tasks")) 
    
@app.post('/<int:task_id>/update_task/')
def update_task(task_id):
    title= request.form['title']
    list=request.form['list']
    duedate=request.form['duedate']
    updatequery('update todo set title = ?,duedate = ?,list=? where task_id = ? ',(title,duedate,list,task_id))
    logging.info('Task %d updated', task_id) # log the update of the task
    return redirect(url_for("tasks")) 

@app.route('/<int:task_id>/delete_task/')
def delete_task(task_id):    
    updatequery('delete from todo where task_id = ? ',[task_id])    
    logging.info('Task %d deleted', task_id) # log the deletion of the task
    return redirect(url_for("tasks"))

@app.route('/<int:task_id>/<status>/update_status/')
def update_status(task_id,status):
    status=int(status)
    if status==-1:
        status=0
    status=(status+1 )%2
    updatequery('update todo set status = ? where task_id = ? ',(status,task_id))   
    logging.info('Status of task %d updated to %d', task_id, status) # log the update of the task status
    return redirect(url_for("tasks"))

@app.route('/<criteria>/sort_tasks/')
def sort_tasks(criteria):
    logging.info('Sorting tasks by %s', criteria) # log the sorting of tasks
    if session['list']=="All lists":
        tasks=selectquery("select * from todo where username=? order by "+criteria,[session['username']])
    else:
        tasks=selectquery("select * from todo where username=? and list=? order by "+criteria,(session['username'],session['list']))
    lists=selectquery('select * from lists where username=?',[session['username']])
    return render_template("tasks.html",tasks=tasks,lists=lists)

#...................................DOWNLOAD TASKS.........................................................
@app.route('/<tasks>/download')
def download(tasks):
    try:
        tasks = tasks.split(",")
        data = "Title,Due Date,Category,Status,\n"
        for i in range(0, len(tasks), 7):
            data += tasks[i+2].strip()[1:-1] + "," + tasks[i+5].strip()[1:-1] + "," + tasks[i+3].strip()[1:-1] + ","
            if tasks[i+6][1] == '0':
                data += "Not completed,\n"
            else:
                data += "Completed,\n"
        logging.info('User %s downloaded tasks', tasks) # log the download of tasks
        return Response(data, mimetype="txt/csv", headers={"Content-disposition": "attachment;filename=tasks.csv"})
    except Exception as e:
        logging.exception('An error occurred while downloading tasks') # log the exception
        return Response('An error occurred while processing your request', status=500)
#....................................LIST OPERATIONS........................................................
@app.route('/lists')
def lists():
    lists=selectquery("select * from lists where username=? and list_name!='Default'",[session['username']])
    logging.info('Lists page accessed by user %s', session['username']) # log the access of list page
    return render_template("lists.html",lists=lists)
@app.route('/<message>/lists')
def message_to_lists(message):
    lists=selectquery("select * from lists where username=? and list_name!='Default'",[session['username']])
    logging.info('Message "%s" displayed on Lists page for user %s', message, session['username']) # log the message display
    return render_template("lists.html", lists=lists, message=message)
    

@app.route('/<list_name>/change_list/')
def change_list(list_name):
    session['list'] = list_name
    logging.info('List changed to %s', list_name) # log the change of list
    return redirect(url_for('tasks'))

@app.route('/addlist',methods=('GET','POST'))
def addlist():
    list_name = request.form['name']
    data = selectquery("SELECT * FROM lists WHERE list_name=? AND username=?", (list_name, session['username']))
    if data:
        message = "List name already exists"
        logging.warning('List "%s" already exists for user %s', list_name, session['username']) # log the warning
        return redirect(url_for('lists'), message=message)
    updatequery('INSERT INTO lists (list_name, username) VALUES (?, ?)', (list_name, session['username']))
    logging.info('New list "%s" added for user %s', list_name, session['username']) # log the addition of new list
    return redirect(url_for('lists'))

@app.post('/<int:list_id>/updatelist/')
def update_list(list_id):
    list_name= request.form['name'] 
    updatequery("update todo set list=? where username=?",(list_name,session['username']))
    updatequery("update lists set list_name = ? where list_id = ?",(list_name,list_id))
    logging.info('List "%s" updated for user %s', list_name, session['username']) # log the update of the list
    return redirect(url_for("lists"))  

@app.route('/<list_name>/deletelist/')
def deletelist(list_name):
    updatequery('delete from lists where list_name = ? and username = ?',(list_name,session['username']))
    updatequery('delete from todo where username=? and list=?',(session['username'],list_name))
    logging.info('List "%s" deleted for user %s', list_name, session['username']) # log the deletion of the list
    return redirect(url_for('lists'))

#.................................FINISHED TASKS....................................................................

@app.route('/finished_tasks',methods=('GET','POST'))
def finished_tasks():
    lists=selectquery('select * from lists where username=?',[session['username']])
    if request.method=='POST':
        search=request.form['search']
        search="%"+search+"%"
        tasks=selectquery("select * from todo where username like ? and (title like ? or duedate like ? or list like ?) and status=1",(session['username'],search,search,search))
        return render_template("searchtask.html",tasks=tasks,lists=lists) 
    else:
        tasks=selectquery('select * from todo where username=? and status=1',[session['username']]) 
        return render_template("finished_tasks.html",tasks=tasks,lists=lists)

@app.route('/<criteria>/sort_finished_tasks/')
def sort_finished_tasks(criteria):
    logging.info('Sorting tasks by %s', criteria) # log the sorting of tasks
    tasks=selectquery("select * from todo where username=? and status=1 order by "+criteria,[session['username']])
    lists=selectquery('select * from lists where username=?',[session['username']])
    return render_template("finished_tasks.html",tasks=tasks,lists=lists) 

@app.route('/<task_id>/delete_finished_task/')
def delete_finished_task(task_id):
    updatequery('delete from todo where username=? and task_id=?',(session['username'],task_id))
    return redirect(url_for("finished_tasks"))

@app.route('/<task_id>/update_finished_status/')
def update_finished_status(task_id):
    updatequery('update todo set status =0 where username=? and task_id=?',(session['username'],task_id))
    return redirect(url_for("finished_tasks"))
#.................................USER LOGOUT.......................................................................
@app.route("/logout")
def logout():
    ''' Clears the session and redirects to login'''
    try:
        # Clearing the session
        session.clear()        
        # Redirecting to login page
        return redirect(url_for('login'))

    except Exception as e:
        # Logging the error message
        logger.error(f"Error in logout(): {str(e)}")        
        # Redirecting to error page
        return redirect(url_for('error'))


if __name__ == '__main__':
    try:
        app.run()
    except Exception as e:
        # Logging the error message
        logger.error(f"Error in main: {str(e)}")