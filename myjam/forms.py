from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField
from flask.ext.security.forms import RegisterForm, ChangePasswordForm, ResetPasswordForm


class MJRegisterForm(RegisterForm):
    """
    RegisterForm without a second 'confirm-password' field.
    """
    def __init__(self, *args, **kwargs):
        RegisterForm.__init__(self, *args, **kwargs)
        del self.password_confirm


class MJChangePasswordForm(ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        ChangePasswordForm.__init__(self, *args, **kwargs)
        del self.new_password_confirm


class MJResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        ResetPasswordForm.__init__(self, *args, **kwargs)
        del self.password_confirm

class RecipeSearchForm(Form):
    query = StringField('Ingredients')


class ArticleForm(Form):
    title = StringField('Title',
                        validators=[DataRequired('Must have a title')])
    text = PageDownField()
