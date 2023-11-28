import secrets
import os

from flask import (
    Flask, render_template,
    url_for, redirect, request, flash, jsonify, g
)

from database_persistence import DatabasePersistence

from utils import (
    error_for_list_name, error_for_todo, list_class, is_list_completed,
    todos_remaining_count, todos_count, sort_items, is_todo_completed
)

from exceptions import ListNotFoundError

app = Flask(__name__)

app.secret_key = secrets.token_hex(32)

@app.context_processor
def list_utilities_processor():
    return dict(is_list_completed=is_list_completed,
                list_class=list_class, todos_count=todos_count,
                todos_remaining_count=todos_remaining_count,
                sort_items=sort_items, is_todo_completed=is_todo_completed
            )

@app.errorhandler(ListNotFoundError)
def handle_list_not_found_error(error):
    flash(error.message, "error")
    return redirect(url_for('show_lists'))

@app.before_request
def load_storage():
    g.storage = DatabasePersistence()

@app.route("/")
def index():
    return redirect(url_for('show_lists'))

@app.route("/lists", methods=["GET"])
def show_lists():
    lists = g.storage.all_lists()
    return render_template('lists.html', lists=lists)

@app.route("/lists", methods=["POST"])
def create_list():
    name = request.form["list_name"].strip()
    error = error_for_list_name(name, g.storage.all_lists())
    if error:
        flash(error, "error")
        return render_template('new_list.html')
    g.storage.create_new_list(name)
    flash("The list has been created.", "success")
    return redirect(url_for('show_lists'))

@app.route("/lists/new")
def add_list():
    return render_template('new_list.html')

@app.route("/lists/<int:list_id>", methods=["GET"])

def show_list(list_id):
    lst = g.storage.find_list(list_id)
    if not lst:
        raise ListNotFoundError(f"The specified list with id {list_id} was not found.")
    return render_template('list.html', list=lst, list_id=list_id)

@app.route("/lists/<int:list_id>", methods=["POST"])

def update_list(list_id):
    name = request.form["list_name"].strip()
    lst = g.storage.find_list(list_id)
    print(lst)
    error = error_for_list_name(name, g.storage.all_lists())
    print(error)
    if error:
        flash(error, "error")
        return render_template('edit_list.html', list=lst)
    print("here")
    g.storage.update_list_name(list_id, name)
    flash("The list has been updated.", "success")
    return redirect(url_for('show_lists'))

@app.route("/lists/<int:list_id>/edit")

def edit_list(list_id):
    lst = g.storage.find_list(list_id)
    if not lst:
        raise ListNotFoundError(f"The specified list with id {list_id} was not found.")
    return render_template('edit_list.html', list=lst)

@app.route("/lists/<int:list_id>/delete", methods=["POST"])

def delete_list(list_id):
    g.storage.delete_list(list_id)
    flash("The list has been deleted.", "success")
    return redirect(url_for('show_lists'))

@app.route("/lists/<int:list_id>/todos", methods=["POST"])

def create_todo(list_id):
    todo_name = request.form["todo"].strip()
    lst = g.storage.find_list(list_id)

    error = error_for_todo(todo_name)
    if error:
        flash(error, "error")
        return render_template('list.html', list=lst, list_id=list_id)
    g.storage.create_new_todo(list_id, todo_name)
    flash("The todo was added.", "success")
    return redirect(url_for('show_list', list_id=list_id))

@app.route("/lists/<int:list_id>/todos/<int:todo_id>/delete", methods=["POST"])
def delete_todo(list_id, todo_id):
    g.storage.delete_todo_from_list(list_id, todo_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)
    else:
        flash("The todo has been deleted.", "success")
        return redirect(url_for('show_list', list_id=list_id))

@app.route("/lists/<int:list_id>/todos/<int:todo_id>", methods=["POST"])

def update_todo_status(list_id, todo_id):
    is_completed = request.form['completed'] == 'True'
    g.storage.update_todo_status(list_id, todo_id, is_completed)

    flash("The todo has been updated.", "success")
    return redirect(url_for('show_list', list_id=list_id))

@app.route("/lists/<int:list_id>/complete_all", methods=["POST"])

def mark_all_todos_completed(list_id):
    g.storage.mark_all_todos_as_completed(list_id)

    flash("All todos have been updated.", "success")
    return redirect(url_for('show_list', list_id=list_id))

if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(debug=False)
    else:
        app.run(debug=True, port=5003)