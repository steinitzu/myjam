from flask import redirect, render_template, url_for, flash, request
from flask import send_from_directory
from flask.ext.security import login_required, current_user
from sqlalchemy.sql import text

from . import app, db
from .forms import ArticleForm, RecipeSearchForm
from .models import Article, Recipe, Image
from .search import recipe_search
from .util import safe_cast
from . import log


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'alert-danger')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/testers', methods=['GET'])
def testers():
    return render_template('testers.html')


@app.route('/recipes', methods=['GET', 'POST'])
def get_recipes():
    query = request.args.get('query')
    page = safe_cast(request.args.get('page'), int, 1)
    form = RecipeSearchForm(request.form)
    if form.validate_on_submit():
        return redirect(url_for('get_recipes', query=form.query.data))
    elif query:
        paginate = recipe_search(query).paginate(page, 12)
        form.query.data = query
    else:
        paginate = Recipe.query.order_by(Recipe.name).paginate(page, 12)
    recipes = paginate.items
    return render_template('recipe_search.html',
                           form=form, recipes=recipes,
                           paginate=paginate)


@app.route('/image/<image_id>')
def get_image(image_id):
    image = Image.query.filter_by(id=image_id).first()
    return send_from_directory(image.directory, image.filename)


@app.route('/images')
def get_images():
    images = [i.id for i in Image.query.all()]
    return render_template('images.html', images=images)


@app.route('/articles/create', methods=['GET', 'POST'])
@login_required
def create_article():
    form = ArticleForm(request.form)
    if form.validate_on_submit():
        article = Article(
            title=form.title.data,
            text=form.text.data,
            site_user=current_user)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('articles/create.html', form=form)


@app.route('/articles/view/<article_id>', methods=['GET'])
def view_article(article_id):
    article = Article.query.filter_by(id=article_id).first()
    return render_template('articles/view.html', article=article)
