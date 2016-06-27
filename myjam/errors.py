class FailedToCreateUser(Exception):
    def __init__(self, username=None, email=None, message=None):
        if not message:
            message = 'Failed to create user named: "{}" with email: "{}"'.format(
                username, email)
        self.username = username
        self.email = email
        Exception.__init__(self, message)


class DuplicateUsername(FailedToCreateUser):
    def __init__(self, username):
        msg = 'Username: "{}" is already in use.'.format(username)
        FailedToCreateUser.__init__(self,
                                    username=username,
                                    message=msg)


class DuplicateEmail(FailedToCreateUser):
    def __init__(self, email):
        msg = 'This email: "{}" is already registered.'.format(email)
        FailedToCreateUser.__init__(self, email=email, message=msg)


class UserNotFound(Exception):
    def __init__(self, id=None, username=None, email=None):
        self.id = id
        self.username = username
        self.email = email
        Exception.__init__('User was not found in database')


class NoSuchUser(Exception):
    pass


class UserNotActivate(Exception):
    pass


class IncorrectPassword(Exception):
    pass
