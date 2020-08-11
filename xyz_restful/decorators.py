# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals


def register(**kwargs):
    the_path = kwargs.pop('path', None)
    def _model_view_set_wrapper(viewset_class):
        m = viewset_class.queryset is not None and viewset_class.queryset.model or viewset_class.serializer_class.Meta.model
        path = the_path or '%s/%s' % (m._meta.app_label, getattr(m, 'alias', m._meta.model_name).lower())
        from .helper import router
        router.register(path, viewset_class, **kwargs)
        return viewset_class

    return _model_view_set_wrapper
