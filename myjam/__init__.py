import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_pagedown import PageDown
from flask.ext.markdown import Markdown
from flask_bootstrap import Bootstrap
from flask_bootstrap.nav import BootstrapRenderer
from flask_nav import Nav, register_renderer
from flask_nav.elements import Navbar, View, Subgroup
from flask.ext.security import SQLAlchemyUserDatastore, Security, current_user
from flask_mail import Mail

from .food2fork import Food2Fork

log = logging.getLogger('myjam')
log.addHandler(logging.StreamHandler())

# Create app
app = Flask(__name__)

# Set up app config
app.config.from_pyfile('config.py')
app.config.from_envvar('MYJAM_CONFIG_PATH')

log.setLevel(
    logging.DEBUG if app.config['DEBUG'] else logging.WARNING)

# Init db
db = SQLAlchemy(app)

# Register pagedown extension
pagedown = PageDown(app)

# Register markdown extension (required by pagedown)
markdown = Markdown(app, extensions=['fenced_code'])

# Register bootstrap extension
bootstrap = Bootstrap(app)

# Register flask-nav extension
nav = Nav(app)

# Register flask-mail extension (credentials from config)
mail = Mail(app)

# Set up food2fork api
f2f = Food2Fork(app.config['FOOD2FORK_API_KEY'],
                search_url=app.config['FOOD2FORK_SEARCH_URL'],
                get_url=app.config['FOOD2FORK_GET_URL'],
                cache=app.config['FOOD2FORK_USE_CACHE'],
                cache_expire_after=app.config['FOOD2FORK_CACHE_EXPIRE_AFTER'])

# Set up flask-security
# Importing from models here because db must be initialized first
from .models import SiteUser, Role
from .forms import MJRegisterForm, MJChangePasswordForm, MJResetPasswordForm
user_datastore = SQLAlchemyUserDatastore(db, SiteUser, Role)
security = Security(app, user_datastore,
                    register_form=MJRegisterForm,
                    change_password_form=MJChangePasswordForm,
                    reset_password_form=MJResetPasswordForm)

# Importing views to declare methods
from . import views


# set up navbar and fixed_top renderer
@nav.navigation()
def navbar():
    items = [View('Myjam', 'index')]
    # s = Subgroup('My account',
    #     View('Log in', 'security.login')
    if current_user.is_authenticated:
        s = Subgroup('My account',
                     View('Change password', 'security.change_password'),
                     View('Log out', 'security.logout'))
        items.append(s)

    else:
        items.append(View('Log in', 'security.login'))
        items.append(View('Register', 'security.register'))
    return Navbar(*items)


class FixedTopRenderer(BootstrapRenderer):
    """
    Overrides default bootstrap renderer by adding
    the 'navbar-fixed-top' css tag to html.
    """

    def visit_Navbar(self, node):
        root = BootstrapRenderer.visit_Navbar(self, node)
        root['class'] = 'navbar navbar-default navbar-fixed-top'
        return root

register_renderer(app, 'fixed_top', FixedTopRenderer)


# App startup
@app.before_first_request
def create_user():
    #db.drop_all()
    db.create_all()


if __name__ == '__main__':
    app.run()
