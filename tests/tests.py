
from datetime import date

from django.test import TestCase

from .models import Author, Book

import django_selector as ds

class FilterSet(ds.FilterSet):

    year = ds.CharFilter(label='Datum', name='date__year', lookup_expr='exact')
    title = ds.CharFilter(label='Titel')
    author = ds.CharFilter(label='Author', name='author__name')

    author_or_title = ds.CharFilter(name=['author__name', 'title'])

    min_date = ds.DateFilter(label='Ab Datum', name='date', lookup_expr='gte')

class Tests(TestCase):

    @classmethod
    def setUpTestData(cls):
        kafka = Author.objects.create(name='Kafka')
        boell = Author.objects.create(name='Böll')

        Book.objects.create(
            author = kafka,
            date = date(1922, 1, 1),
            title = 'Das Schloss',
        )

        Book.objects.create(
            author = kafka,
            date = date(1914, 1, 1),
            title = 'Der Prozess',
        )

        Book.objects.create(
            author = boell,
            date = date(1963, 1, 1),
            title = 'Ansichten eines Clowns',
        )

    def test_filters_in_filterset(self):

        filters = FilterSet.filters

        self.assertFalse(hasattr(FilterSet, 'author'))

        self.assertEqual(filters['author'].name, 'author__name')
        self.assertEqual(filters['title'].lookup_expr, 'icontains')
        self.assertEqual(filters['year'].name, 'date__year')

    def test_filter_queryset_with_filter(self):
        filters = FilterSet.filters
        qs = Book.objects.all()

        self.assertEqual(filters['author'].filter(qs, 'kafka').count(), 2)
        self.assertEqual(filters['title'].filter(qs, 'clown').count(), 1)
        self.assertEqual(filters['year'].filter(qs, '1922').count(), 1)

        self.assertEqual(filters['min_date'].filter(qs, date(1950, 1, 1)).count(), 1)

    def test_filter_queryset_with_filterset(self):
        qs = Book.objects.all()

        f = FilterSet(data={}, queryset=qs)
        self.assertEqual(f.qs.count(), 3)

        f = FilterSet(data={'author': 'kafka'}, queryset=qs)
        self.assertEqual(f.qs.count(), 2)

        f = FilterSet(data={'title': 'clown'}, queryset=qs)
        self.assertEqual(f.qs.count(), 1)
        
        f = FilterSet(data={'year': '1922'}, queryset=qs)
        self.assertEqual(f.qs.count(), 1)

        f = FilterSet(data={'min_date': '1.1.1950'}, queryset=qs)
        self.assertEqual(f.qs.count(), 1)

        f = FilterSet(data={'author_or_title': 'kafka'}, queryset=qs)
        self.assertEqual(f.qs.count(), 2)

        f = FilterSet(data={'author_or_title': 'clown'}, queryset=qs)
        self.assertEqual(f.qs.count(), 1)
