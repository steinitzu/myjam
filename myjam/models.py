from datetime import datetime
import os

from sqlalchemy import exists, event, DDL
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils.types.password import PasswordType
from sqlalchemy_utils import EmailType
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship
from flask.ext.security import UserMixin, RoleMixin

from . import db, app


def row_exists(model_class, field, value):
    return db.session.query(exists().where(
        getattr(model_class, field)==value)).scalar()


class BaseModel(object):
    """
    Columns and functions that every model will have in common.
    Subclass this along with desired sqlalchemy model decleration.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_created = db.Column(db.DateTime,
                             server_default=func.current_timestamp())
    time_modified = db.Column(db.DateTime,
                              server_default=func.current_timestamp(),
                              onupdate=func.current_timestamp())


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('site_user.id')),
                       db.Column('role_id', db.Integer(),
                                 db.ForeignKey('role.id')))


class Role(BaseModel, db.Model, RoleMixin):
    __tablename__ = 'role'
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.String(300))


class SiteUser(BaseModel, db.Model, UserMixin):
    __tablename__ = 'site_user'
    #username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(EmailType, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    # password = db.Column(PasswordType(max_length=128,
    #                                   schemes=['pbkdf2_sha512', 'md5_crypt']))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    articles = relationship('Article', back_populates='site_user')
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    # @property
    # def is_active(self):
    #     return self.active

    # def is_authenticated(self):
    #     return True

    # def is_anonymous(self):
    #     return False

    # def get_id(self):
    #     return self.username


class Recipe(BaseModel, db.Model):
    __tablename__ = 'recipe'
    site_time_published = db.Column(db.DateTime(), nullable=False)
    site_time_modified = db.Column(db.DateTime(), nullable=False)
    url = db.Column(db.String(), nullable=False, unique=True)
    #image = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False)
    author = db.Column(db.String(), nullable=False)
    recipe_yield = db.Column(db.String())
    recipe_category = db.Column(db.String())
    recipe_cuisine = db.Column(db.String())
    cook_time = db.Column(db.Interval())
    prep_time = db.Column(db.Interval())
    total_time = db.Column(db.Interval())
    image_id = db.Column(db.Integer(), ForeignKey('image.id'))
    image = relationship('Image')
    ingredients = relationship('Ingredient', back_populates='recipe')


class Ingredient(BaseModel, db.Model):
    __tablename__ = 'ingredient'
    name = db.Column(db.String())
    recipe_id = db.Column(db.Integer(),
                          ForeignKey('recipe.id'), nullable=False)
    recipe = relationship('Recipe', back_populates='ingredients')


class Image(BaseModel, db.Model):
    __tablename__ = 'image'
    file_extension = db.Column(db.String(4))

    @property
    def directory(self):
        strid = str(self.id)
        folder = '0' if self.id < 1000 else strid[0]
        path = os.path.join(
            app.config['UPLOAD_PATH'],
            folder)
        return path

    @property
    def filename(self):
        return str(self.id)


class Article(BaseModel, db.Model):
    __tablename__ = 'article'
    title = db.Column(db.String(384), nullable=False)
    text = db.Column(db.String(), nullable=False)
    site_user_id = db.Column(db.Integer(), ForeignKey('site_user.id'), nullable=False)
    site_user = relationship('SiteUser', back_populates='articles')


event.listen(
    Ingredient.__table__,
    "after_create",
    DDL("""
        CREATE OR REPLACE VIEW ingredient_view
        AS SELECT recipe_id, string_agg(name, ', ')
        AS ingredients
        FROM ingredient
        GROUP BY recipe_id;
        """).execute_if(dialect='postgresql'))

event.listen(
    Ingredient.__table__,
    "before_drop",
    DDL("""
        DROP VIEW IF EXISTS ingredient_view;
        """).execute_if(dialect='postgresql'))
