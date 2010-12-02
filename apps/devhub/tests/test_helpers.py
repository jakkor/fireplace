import unittest

from django.utils import translation

from mock import Mock
from nose.tools import eq_
from pyquery import PyQuery as pq

from amo.urlresolvers import reverse
from amo.tests.test_helpers import render


def test_dev_page_title():
    translation.activate('en-US')
    request = Mock()
    request.APP = None
    addon = Mock()
    addon.name = 'name'
    ctx = {'request': request, 'addon': addon}

    title = 'Oh hai!'
    s1 = render('{{ dev_page_title("%s") }}' % title, ctx)
    s2 = render('{{ page_title("%s :: Developer Hub") }}' % title, ctx)
    eq_(s1, s2)

    s1 = render('{{ dev_page_title() }}', ctx)
    s2 = render('{{ page_title("Developer Hub") }}', ctx)
    eq_(s1, s2)

    s1 = render('{{ dev_page_title("%s", addon) }}' % title, ctx)
    s2 = render('{{ page_title("%s :: %s") }}' % (title, addon.name), ctx)
    eq_(s1, s2)


class TestDevBreadcrumbs(unittest.TestCase):

    def setUp(self):
        self.request = Mock()
        self.request.APP = None

    def test_no_args(self):
        s = render('{{ dev_breadcrumbs() }}', {'request': self.request})
        doc = pq(s)
        crumbs = doc('li')
        eq_(len(crumbs), 2)
        eq_(crumbs.text(), 'Developer Hub My Add-ons')
        eq_(crumbs.eq(1).children('a'), [])

    def test_no_args_with_default(self):
        s = render('{{ dev_breadcrumbs(add_default=True) }}',
                   {'request': self.request})
        doc = pq(s)
        crumbs = doc('li')
        eq_(crumbs.text(), 'Add-ons Developer Hub My Add-ons')
        eq_(crumbs.eq(1).children('a').attr('href'), reverse('devhub.index'))
        eq_(crumbs.eq(2).children('a'), [])

    def test_with_items(self):
        s = render("""{{ dev_breadcrumbs(items=[('/foo', 'foo'),
                                                ('/bar', 'bar')]) }}'""",
                  {'request': self.request})
        doc = pq(s)
        crumbs = doc('li>a')
        eq_(len(crumbs), 4)
        eq_(crumbs.eq(2).text(), 'foo')
        eq_(crumbs.eq(2).attr('href'), '/foo')
        eq_(crumbs.eq(3).text(), 'bar')
        eq_(crumbs.eq(3).attr('href'), '/bar')

    def test_with_addon(self):
        addon = Mock()
        addon.name = 'Firebug'
        addon.id = 1843
        s = render("""{{ dev_breadcrumbs(addon) }}""",
                   {'request': self.request, 'addon': addon})
        doc = pq(s)
        crumbs = doc('li')
        eq_(crumbs.text(), 'Developer Hub My Add-ons Firebug')
        eq_(crumbs.eq(1).text(), 'My Add-ons')
        eq_(crumbs.eq(1).children('a').attr('href'), reverse('devhub.addons'))
        eq_(crumbs.eq(2).text(), 'Firebug')
        eq_(crumbs.eq(2).children('a'), [])

    def test_with_addon_and_items(self):
        addon = Mock()
        addon.name = 'Firebug'
        addon.id = 1843
        s = render("""{{ dev_breadcrumbs(addon,
                                         items=[('/foo', 'foo'),
                                                ('/bar', 'bar')]) }}""",
                   {'request': self.request, 'addon': addon})
        doc = pq(s)
        crumbs = doc('li')
        eq_(len(crumbs), 5)
        eq_(crumbs.eq(2).text(), 'Firebug')
        eq_(crumbs.eq(2).children('a').attr('href'),
            reverse('devhub.addons.edit', args=[addon.id]))
        eq_(crumbs.eq(3).text(), 'foo')
        eq_(crumbs.eq(3).children('a').attr('href'), '/foo')
        eq_(crumbs.eq(4).text(), 'bar')
        eq_(crumbs.eq(4).children('a').attr('href'), '/bar')
