# -*- coding:utf-8 -*-
from rest_framework import decorators, response, status, exceptions
from .signals import batch_action_post
__author__ = 'denishuang'

from six import string_types


class RestCreateMixin(object):
    def get_serializer_save_args(self):
        return {}

    def perform_create(self, serializer):
        serializer.save(**self.get_serializer_save_args())


class UserApiMixin(RestCreateMixin):
    user_field_name = 'user'

    def get_serializer_save_args(self):
        d = super(UserApiMixin, self).get_serializer_save_args()
        d[self.user_field_name] = self.request.user
        return d


class ProtectDestroyMixin(object):

    def handle_exception(self, exc):
        from django.db.models import ProtectedError
        if isinstance(exc, ProtectedError):
            exc = exceptions.MethodNotAllowed(self.request.method, detail='请先删除全部关联资料')
        return super(ProtectDestroyMixin, self).handle_exception(exc)


class IDAndStrFieldSerializerMixin(object):
    def get_field_names(self, declared_fields, info):
        fns = super(IDAndStrFieldSerializerMixin, self).get_field_names(declared_fields, info)
        fns += ('id', '__str__')
        return fns


class BatchActionMixin(object):

    def do_batch_action(self, field_name, default=None, extra_params={}):
        r = self.request
        qset = self.filter_queryset(self.get_queryset())
        scope = r.data.get('scope')
        if scope != 'all':
            ids = r.data.get('batch_action_ids')
            if scope == 'exclude':
                qset = qset.exclude(id__in=ids)
            else:
                qset = qset.filter(id__in=ids)
        rows = 0
        if isinstance(field_name, string_types):
            d = {field_name: r.data.get(field_name, default)}
            d.update(extra_params)
            rows = qset.update(**d)
        elif callable(field_name):
            rows = len(qset)
            for a in qset:
                field_name(a)
        batch_action_post.send_robust(sender=qset.model, queryset=qset, field_name=field_name, default=default)
        return response.Response({'rows': rows})
