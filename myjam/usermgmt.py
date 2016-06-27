from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

import psycopg2.errorcodes as errorcodes
from flask import url_for, render_template

from .models import SiteUser
from . import db
from .errors import DuplicateUsername, DuplicateEmail, UserNotFound
from .util import ts, send_email


def create_user(username, email, password):
    user = SiteUser(
        username=username,
        email=email,
        password=password)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as e:
        # Get the original exception from psycopg2
        oe = e.orig
        if oe.pgcode == errorcodes.UNIQUE_VIOLATION:
            if oe.diag.constraint_name == 'site_user_username_key':
                raise DuplicateUsername(username)
            elif oe.diag.constraint_name == 'site_user_email_key':
                raise DuplicateEmail(email)
            else:
                raise
        else:
            raise
    return user


def send_confirmation_email(user):
    subject = 'Confirm your email'
    token = ts.dumps(user.email, salt='email-confirm-key')
    confirm_url = url_for(
        'confirm_email',
        token=token,
        _external=True)
    html = render_template(
        'email/activate.html',
        confirm_url=confirm_url)
    send_email(user.email, subject, html)


def get_user(id=None, username=None, email=None):
    """
    Returns user with corresponding id, username or email
    (whichever matches first).
    """
    user = SiteUser.query.filter(or_(
        id == id, username == username, email == email)).first()
    if user:
        return user
    else:
        raise UserNotFound(id=id, username=username, email=email)
