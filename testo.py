import unittest
import sys

from myjam import search


class TestQuery(object):
    def __init__(self, query, result):
        self.query = query
        self.result = result

class PreParserTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def iterassert(self, func, queries):
        """
        Accepts a function and a list of |TestQuery| like objects.
        Calls |assertEquals(query.result, func(query.query))| for each
        query in queries.
        """
        for i, q in enumerate(queries):
            result = func(q.query)
            msg = 'Query:{}:"{}" Expected:"{}", got:"{}"'.format(
                i, q.query, q.result, result)
            self.assertEqual(q.result, result, msg=msg)


    def test_commas_to_spaces(self):
        queries = (
            TestQuery(',,,,,,', ''),
            TestQuery('garlic, tomato, eggplant',
                      'garlic  tomato  eggplant'),
            TestQuery(',garlic,tomato,eggplant',
                      'garlic tomato eggplant'),
            )
        self.iterassert(search.commas_to_spaces, queries)

    def test_remove_leading_tokens(self):
        queries = (
            TestQuery('and or not and garlic and eggplant',
                      'garlic and eggplant'),
            TestQuery('not and or garlic and eggplant',
                      'not garlic and eggplant'),
            TestQuery('or not not not and and  and or not garlic and eggplant',
                      'garlic and eggplant'),
            TestQuery('not not not not garlic and eggplant',
                      'not garlic and eggplant'),
            TestQuery('and and and and garlic and eggplant',
                      'garlic and eggplant'),
        )
        self.iterassert(search.remove_leading_tokens, queries)

    def test_remove_trailing_tokens(self):
        queries = (
            TestQuery('garlic and eggplant and not or',
                      'garlic and eggplant'),
            TestQuery('garlic and eggplant not not not',
                      'garlic and eggplant'),
            TestQuery('garlic and eggplant and',
                      'garlic and eggplant'),
            TestQuery('or not and or not',
                      ''),
        )
        self.iterassert(search.remove_trailing_tokens, queries)

    def test_remove_duplicate_tokens(self):
        queries = (
            TestQuery('garlic and and eggplant',
                      'garlic and eggplant'),
            TestQuery('garlic and or or eggplant',
                      'garlic and or eggplant'),
            TestQuery('garlic and and and eggplant',
                      'garlic and eggplant'),
            TestQuery('garlic and eggplant',
                      'garlic and eggplant'),
        )
        self.iterassert(search.remove_duplicate_tokens, queries)

    def test_pre_parse(self):
        t = TestQuery
        queries = (
            t('garlic and eggplant',
              'garlic&eggplant'),
            t('garlic eggplant',
              'garlic&eggplant'),
            t('garlic, eggplant',
              'garlic&eggplant'),
            t('garlic,eggplant',
              'garlic&eggplant'),
            t('garlic or eggplant',
              'garlic|eggplant'),
            t('garlic and or eggplant',
              'garlic|eggplant'),
            t('not garlic and eggplant',
              '!garlic&eggplant'),
            t('not and or garlic and eggplant',
              '!garlic&eggplant'),
            t('garlic and not eggplant',
              'garlic&!eggplant'),
            t('not and or not and or not',
              ''),
            t('eggplant', 'eggplant'),
            t('(@)#*@(#*@)(#*)@', ''),
        )
        self.iterassert(search.pre_parse, queries)




def main(argv=sys.argv):
    unittest.main()

if __name__ == '__main__':
    main()
