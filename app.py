from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from datetime import timedelta


app = Flask(__name__)

# Connect to MongoDB server
client = MongoClient('localhost', 27017)

# Get the 'flask_db' database from the MongoDB server
db = client.flask_db
# Get the 'todos' collection from the 'flask_db' database
todos = db.todos


def GetEachTimes(times, repeat):
    # Get the task details from the form
    # A function that returns a list of datetime objects that represent the due dates
    # of a task with a given repeat frequency and number of times to repeat
    if repeat == 'month':
        delta = 30
    elif repeat == 'week':
        delta = 7
    else:
        delta = 1
    today = datetime.today()
    res = [today]
    for i in range(1, int(times)):
        res.append(today + timedelta(days=i*delta))
    return res


# The default route that shows a list of all the tasks
@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        # Get the task details from the form
        content = request.form['content']
        repeat = request.form['repeat']
        times = request.form['times']
        degree = request.form['degree']
        # Insert the task into the 'todos' collection for each due date
        for d in GetEachTimes(times, repeat):
            todos.insert_one(
                {'content': content, 'degree': degree, 'date': d})
        # Redirect to the default route after submitting the form
        return redirect(url_for('index'))

    # Get all the tasks from the 'todos' collection and sort them by degree of importance
    all_todos = todos.find()
    tasks = all_todos
    sorted_tasks = sorted(tasks, key=lambda todo: todo['degree'])
    # Render the HTML template to show the list of tasks
    return render_template('index.html', todos=sorted_tasks)


# A route that deletes a task with the given ID
@app.post('/<id>/delete/')
def delete(id):
    todos.delete_one({"_id": ObjectId(id)})
    # Redirect to the default route after deleting the task
    return redirect(url_for('index'))


# A route that shows a form to edit the details of a task with the given ID
@app.route('/<id>/edit', methods=('GET', 'POST'))
def edit(id):
    todo = todos.find_one({'_id': ObjectId(id)})
    if request.method == 'POST':
        # Convert the date string to a datetime object
        date_str = request.form['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        # Update the task details in the 'todos' collection
        todos.update_one({'_id': ObjectId(id)},
                         {'$set': {'content': request.form['content'], 'degree': request.form['degree'], 'date': date_obj}})
        # Redirect to the default route after editing the
        return redirect(url_for('index'))

    # Render the HTML template to show the form for editing the task details
    return render_template('edit.html', todo=todo)


# A route that shows the search results for a given query
@app.route('/search')
def search():
    query = request.args.get('query')
    # Search for tasks in the 'todos' collection whose content matches the query
    results = todos.find({'content': {'$regex': '^' + query, '$options': 'i'}})
    return render_template('search.html', results=results, query=query)


if __name__ == '__main__':
    app.run()
