# coding: utf-8

import unittest
from hamcrest import *

from plant import *

class ConventionalDictTest(unittest.TestCase):
    def test_unicode_keys(self):
        d = ConventionalDict({u'unicodekey': 0})
        assert_that(d.unicodekey, is_(0))
        assert_that(d.has_unicodekey, is_(True))

    def test_has_predicate(self):
        d = ConventionalDict({'key1': 0})
        assert_that(d.has_key1, is_(True))
        assert_that(d.has_key2, is_(False))
        assert_that(d.has_key('key1'), is_(True))
        assert_that(d.has_key('key2'), is_(False))

