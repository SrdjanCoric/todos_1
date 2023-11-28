from flask import (
    Flask, session, render_template,
    url_for, redirect, request, flash, jsonify
)

from utils import (
    error_for_list_name, error_for_todo, list_class, is_list_completed,
    todos_remaining_count, todos_count, sort_items, is_todo_completed,
    find_todo_by_id, find_list_by_id
)

from uuid import uuid4

from exceptions import ListNotFoundError

app = Flask(__name__)

app.secret_key = 'my secret'

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
def initialize_session():
    if 'lists' not in session:
        session['lists'] = []

@app.route("/")
def index():
    return redirect(url_for('show_lists'))

@app.route("/lists", methods=["GET"])
def show_lists():
    lists = session['lists']
    return render_template('lists.html', lists=lists)

@app.route("/lists", methods=["POST"])
def create_list():
    name = request.form["list_name"].strip()
    error = error_for_list_name(name, session['lists'])
    if error:
        flash(error, "error")
        return render_template('new_list.html')
    list_id = str(uuid4())
    session['lists'].append({'id': list_id, 'name': name, 'todos': []})
    flash("The list has been created.", "success")
    session.modified = True
    return redirect(url_for('show_lists'))

@app.route("/lists/new")
def add_list():
    return render_template('new_list.html')

@app.route("/lists/<id>", methods=["GET"])
def show_list(id):
    lst = find_list_by_id(session['lists'], id)
    if not lst:
        raise ListNotFoundError(f"The specified list with id {id} was not found.")
    return render_template('list.html', list=lst, list_id=id)

@app.route("/lists/<id>", methods=["POST"])
def update_list(id):
    name = request.form["list_name"].strip()
    lst = find_list_by_id(session['lists'], id)
    if not lst:
        raise ListNotFoundError(f"The specified list with id {id} was not found.")
    error = error_for_list_name(name, session['lists'])
    if error:
        flash(error, "error")
        return render_template('edit_list.html', list=lst)
    lst['name'] = name
    flash("The list has been updated.", "success")
    session.modified = True
    return redirect(url_for('show_lists'))

@app.route("/lists/<id>/edit")
def edit_list(id):
    lst = find_list_by_id(session['lists'], id)
    if not lst:
        raise ListNotFoundError(f"The specified list with id {id} was not found.")
    return render_template('edit_list.html', list=lst)

@app.route("/lists/<id>/delete", methods=["POST"])
def delete_list(id):
    lists = session['lists']
    for idx in range(len(lists)):
        if lists[idx]['id'] == id:
            del lists[idx]
            break
    flash("The list has been deleted.", "success")
    session.modified = True
    return redirect(url_for('show_lists'))

@app.route("/lists/<list_id>/todos", methods=["POST"])
def create_todo(list_id):
    todo_name = request.form["todo"].strip()
    lst = find_list_by_id(session['lists'], list_id)
    if not lst:
        raise ListNotFoundError(f"The specified list with id {list_id} was not found.")

    error = error_for_todo(todo_name)
    if error:
        flash(error, "error")
        return render_template('list.html', list=lst, list_id=list_id)
    todo_id = str(uuid4())
    lst['todos'].append({'id': todo_id, 'name': todo_name, 'completed': False})
    flash("The todo was added.", "success")
    session.modified = True
    return redirect(url_for('show_list', id=list_id))

@app.route("/lists/<list_id>/todos/<id>/delete", methods=["POST"])
def delete_todo(list_id, id):
    lst = find_list_by_id(session['lists'], list_id)
    if not lst:
        raise ListNotFoundError(f"The specified list with id {id} was not found.")
    for idx, todo in enumerate(lst['todos']):
        if todo['id'] == id:
            del lst['todos'][idx]
            break
    session.modified = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True)
    else:
        flash("The todo has been deleted.", "success")
        return redirect(url_for('show_list', id=list_id))

@app.route("/lists/<list_id>/todos/<id>", methods=["POST"])
def update_todo_status(list_id, id):
    lst = find_list_by_id(session['lists'], list_id)
    if not lst:
        raise ListNotFoundError(f"The specified list with id {id} was not found.")
    is_completed = request.form['completed'] == 'True'

    todo = find_todo_by_id(lst['todos'], id)
    todo['completed'] = is_completed

    flash("The todo has been updated.", "success")
    session.modified = True
    return redirect(url_for('show_list', id=list_id))

@app.route("/lists/<id>/complete_all", methods=["POST"])
def mark_all_todos_completed(id):
    lst = find_list_by_id(session['lists'], id)
    if not lst:
        raise ListNotFoundError(f"The specified list with id {id} was not found.")

    for todo in lst['todos']:
        todo['completed'] = True

    flash("All todos have been updated.", "success")
    session.modified = True
    return redirect(url_for('show_list', id=id))

if __name__ == "__main__":
    app.run(debug=True, port=5003)
