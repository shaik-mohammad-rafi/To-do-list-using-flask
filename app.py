from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'secret123'

client = MongoClient("mongodb://localhost:27017/")
db = client.todo_app
users = db.users
tasks = db.tasks

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        user = users.find_one({'username': uname, 'password': pwd})
        if user:
            session['username'] = uname
            return redirect('/todo')
        else:
            error = "Incorrect credentials. Please try again."
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        if users.find_one({'username': uname}):
            return render_template('signup.html', error='User already exists')
        users.insert_one({'username': uname, 'password': pwd})
        return redirect('/login')
    return render_template('signup.html')

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    if 'username' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        task = request.form['task']
        if task:
            tasks.insert_one({'username': session['username'], 'task': task, 'status': 'pending'})

    pending = list(tasks.find({'username': session['username'], 'status': 'pending'}))
    completed = list(tasks.find({'username': session['username'], 'status': 'completed'}))
    return render_template('todo.html', pending=pending, completed=completed)

@app.route('/complete/<task_id>')
def complete(task_id):
    from bson.objectid import ObjectId
    tasks.update_one({'_id': ObjectId(task_id)}, {'$set': {'status': 'completed'}})
    return redirect('/todo')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
