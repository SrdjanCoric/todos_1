from exceptions import ListNotFoundError

def error_for_list_name(name, lists):
    if not 1 <= len(name) <= 100:
        return "The list name must be between 1 and 100 characters"
    elif any(lst['name'] == name for lst in lists):
        return "The list name must be unique."

    return None

def error_for_todo(name):
    if not 1 <= len(name) <= 100:
        return "Todo name must be between 1 and 100 characters"

    return None

def is_list_completed(lst):
    return len(lst['todos']) > 0 and todos_remaining_count(lst) == 0

def list_class(lst):
    if is_list_completed(lst):
        return "complete"
    return ""

def todos_count(lst):
    return len(lst['todos'])

def todos_remaining_count(lst):
    return sum(1 for todo in lst['todos'] if not todo['completed'])

def is_todo_completed(todo):
    return todo['completed']

def sort_items(items, is_completed):
    incomplete_items = [item for item in items if not is_completed(item)]
    complete_items = [item for item in items if is_completed(item)]

    return incomplete_items + complete_items

def find_todo_by_id(todos, todo_id):
    for todo in todos:
        if todo['id'] == todo_id:
            return todo
    return None
