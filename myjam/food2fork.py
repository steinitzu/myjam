import requests
import requests_cache


class Food2Fork(object):

    def __init__(self, api_key,
                 search_url='http://food2fork.com/api/search',
                 get_url='http://food2fork.com/api/get',
                 cache=True,
                 cache_expire_after=200):
        self.key = api_key
        self.search_url = search_url
        self.get_url = get_url
        if cache:
            requests_cache.install_cache(expire_after=cache_expire_after)

    def search(self, q=None, sort=None, page=None):
        """
        search(q='my search query',
               sort='t'||'r',
               page='1..2.3..4..etc',
               booelan raw (True returns JSON, False returns dict))
        """
        r = requests.get(self.search_url,
                         params={
                             'key': self.key,
                             'q': q,
                             'sort': sort,
                             'page': page})
        return r.json()['recipes']

    def get(self, recipe_id):
        r = requests.get(self.get_url,
                         params={'key': self.key,
                                 'rId': recipe_id})
        return r.json()['recipe']
