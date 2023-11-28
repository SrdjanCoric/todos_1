# exceptions.py

class ListNotFoundError(Exception):

    def __init__(self, message="List not found", *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message


