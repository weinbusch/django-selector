from django.db.models import Q
from django import forms
from functools import reduce

class Filter(object):

    default_lookup_expr = 'exact'
    
    def __init__(self, name='', lookup_expr=None, **kwargs):
        self.name = name
        self.lookup_expr = lookup_expr or self.default_lookup_expr
        self.form_field = self.get_form_field(**kwargs)

    def get_form_field(self, **kwargs):
        return self.form_field_class(required=False, **kwargs)

    def filter(self, qs, value):
        if value:
            # if self.name is a list of values, construct Q queries linked by OR operator
            if isinstance(self.name, (list, tuple)):
                query = reduce(lambda p, q: p|q, [
                    Q(**{name + '__' + self.lookup_expr: value}) for
                        name in self.name
                ])
                return qs.filter(query)
            # else perform a normal queryset.filter operation
            lookup = self.name + '__' + self.lookup_expr
            return qs.filter(**{lookup: value})
        return qs

class CharFilter(Filter):
    default_lookup_expr = 'icontains'
    form_field_class = forms.CharField

class DateFilter(Filter):
    form_field_class = forms.DateField

class ChoiceFilter(Filter):
    form_field_class = forms.TypedChoiceField

class ModelChoiceFilter(Filter):
    form_field_class = forms.ModelChoiceField

class FilterSetMetaClass(type):
    
    def __new__(cls, name, bases, dct):
        dct['filters'] = cls.get_filters(dct)
        return super(cls, FilterSetMetaClass).__new__(cls, name, bases, dct)

    @classmethod
    def get_filters(cls, dct):
        filters ={}
        for name, value in list(dct.items()):
            if isinstance(value, Filter):
                # Add name to each filter
                if not value.name:
                    value.name = name
                # Add to filters dict and remove from class attributes dct
                filters[name] = value
                dct.pop(name)
        return filters

class FilterSet(object, metaclass=FilterSetMetaClass):

    def __init__(self, data, queryset):
        self.data = data
        self._qs = queryset
        self.form_class = self.get_form_class()
        self.form = self.form_class(data)
        self.qs = self.get_filtered_queryset()

    def get_filtered_queryset(self):
        qs = self._qs
        form = self.form
        if form.is_valid():
            for name, filter_ in self.filters.items():
                value = form.cleaned_data.get(name)
                qs = filter_.filter(qs, value)
        return qs

    def get_form_class(self):
        form_fields = self.get_form_fields()
        return type('FilterForm', (forms.Form,), form_fields)

    def get_form_fields(self):
        form_fields = {name: _filter.form_field for name, _filter in self.filters.items()}
        return form_fields