from collections import OrderedDict
import re

from sqlalchemy.sql import text

from .models import Recipe
from . import db, log

ingredient_search_sql = """
SELECT recipe_id
FROM ingredient_view
WHERE to_tsvector(ingredients) @@ to_tsquery(:query);
"""

title_search_sql = """
SELECT id
FROM recipe
WHERE to_tsvector(name) @@ to_tsquery(:query);
"""

match_commas = re.compile(',', re.UNICODE)
match_not_alnum = re.compile('([^\s\w]|_)+', re.UNICODE)
match_spaces = re.compile(' +', re.UNICODE)
match_leading_tokens = re.compile(r'(^|^not)(\b)(and|or|not)\b', re.UNICODE)
match_trailing_token = re.compile(r'(\b|\s)(and|or|not)$', re.UNICODE)

# Not needed anymore
match_duplicate_tokens = re.compile(r'(\band\b|\bor\b|\bnot\b)+', re.UNICODE)


def commas_to_spaces(query):
    return re.sub(match_commas, ' ', query).strip()


def ensure_alnum(query):
    return re.sub(match_not_alnum, '', query)


def remove_multiple_spaces(query):
    return re.sub(match_spaces, ' ', query)


def remove_leading_tokens(query):
    # Assume this is done after converting
    # commas to spaces
    original = query
    while True:
        result = re.sub(match_leading_tokens, r'\1', query).strip()
        if result == query:
            break
        query = result
    # Stick "not" back on front of query if applicable
    # cause I can't regex
    if original.startswith('not ') and query:
        query = 'not ' + query
    return query


def remove_trailing_tokens(query):
    while True:
        # Resub any token at end of query
        result = re.sub(match_trailing_token, '', query)
        # If no change, we're done
        if result == query:
            break
        query = result
    return query


def remove_duplicate_tokens(query):
    s = query.split(' ')
    nlist = []
    lastword = ''
    for word in s:
        if word in ('or', 'and', 'not'):
            if lastword == word:
                continue
        lastword = word
        nlist.append(word)
    return ' '.join(nlist)


def to_pg_tokens(query):
    replacements = (
        ('not ', '!'),
        (' and not ', '&!'),
        (' and or ', '|'),
        (' not and ', '&'),
        (' or and ', '&'),
        (' and ', '&'),
        (' not ', '&!'),
        (' or ', '|'),
        (', ', '&'),
        (',', '&'),
        (' ', '&'),)
    for key, value in replacements:
        query = query.replace(key, value)
    return query


def pre_parse(query):
    log.info(u'User query:"{}"'.format(query))
    query = unicode(query.lower())
    log.info(u'Unicode lowercase query:"{}"'.format(query))
    query = commas_to_spaces(query)
    log.info(u'Commas to spaces query:"{}"'.format(query))
    query = ensure_alnum(query)
    log.info(u'Ensure alnum query:"{}"'.format(query))
    query = remove_multiple_spaces(query)
    log.info(u'Remove multi spaces query:"{}"'.format(query))
    query = remove_leading_tokens(query)
    log.info(u'Remove leading tokens query:"{}"'.format(query))
    query = remove_trailing_tokens(query)
    log.info(u'Remove trailing tokens query:"{}"'.format(query))
    query = remove_duplicate_tokens(query)
    log.info(u'Remove duplicate tokens query:"{}"'.format(query))
    query = to_pg_tokens(query)
    log.info(u'Final query:"{}"'.format(query))
    return query


def recipe_search(user_query):
    query = pre_parse(user_query)
    result1 = db.engine.execute(text(ingredient_search_sql),
                               {'query': query})
    result2 = db.engine.execute(text(title_search_sql),
                                     {'query': query})

    result = set(
        [i[0] for i in result1]
        + [i[0] for i in result2])

    if len(result) == 0:
        return Recipe.query.filter(None)
    recipes = Recipe.query.filter(Recipe.id.in_(result)).order_by(Recipe.name)
#        [i[0] for i in result]))
    return recipes
