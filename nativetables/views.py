from django.core.exceptions import ImproperlyConfigured
from django.views.generic.list import MultipleObjectMixin, ListView

from django.utils import simplejson
import re

from .tables import default_datatable

class DatatableMixin(object):
    '''
    Requires MultipleObjectMixin derivative
    '''
    datatable = None
    context_datatable_name = None

    def get_tranformation_params(self):
        """
        Return a table object to use. The table has automatic support for
        sorting and pagination.
        """
        if self.request.GET.get('datatable', False):
            return simplejson.loads(self.request.GET['datatable'])
        else:
            return self.datatable.initial

    def get_queryset(self):
        """
        Return the datatable queryset class, transformed appropriately.
        """
        if self.datatable is not None:
            datatable = self.datatable
        # elif self.model is not None:
        #     datatable = default_datatable(self.model).all()
        else:
            raise ImproperlyConfigured(u"A datatable class was not specified. Define "
                                       u"%(cls)s.model to use the default or pass in your custom datatable through "
                                       u"%(cls)s.datatable"
                                       % {"cls": type(self).__name__})
        # Give datatable id so it can be referenced in html DOM elements
        datatable.id = self.get_context_object_name(datatable)
        datatable.state = simplejson.dumps(self.get_tranformation_params())
        return datatable.all().transform(**self.get_tranformation_params())

    def get_context_object_name(self, table):
        """
        Get the name to use for the table's template variable.
        If not provided, use underscored version of datatable class name
        """
        if self.context_datatable_name:
            context_datatable_name = self.context_datatable_name
        else:
            context_datatable_name = re.sub('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', '_\\1', table.model.__name__).lower().strip('_') + "_table"
        return context_datatable_name
    
    
    def get_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        queryset = kwargs.pop('object_list')
        context_object_name = self.get_context_object_name(queryset)

        if getattr(queryset,"object_list", False):
            context = {
                'paginator': queryset.paginator,
                'page_obj': queryset,
                'is_paginated': True,
                'object_list': queryset.object_list
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset
            }
        if context_object_name is not None:
            context[context_object_name] = getattr(queryset,"object_list", queryset)
            
        context.update(kwargs)
        return context
        
        # return super(DatatableMixin, self).get_context_data(**context)
       
class DatatableView(DatatableMixin, ListView):
   """
   Generic view that renders a template and passes in a ``Datatable`` object.
   """
   pass