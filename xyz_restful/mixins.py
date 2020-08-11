# -*- coding:utf-8 -*-
from rest_framework import decorators, response, status, exceptions

__author__ = 'denishuang'


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

    def perform_destroy(self, instance):
        from django.db.models import ProtectedError
        try:
            return super(ProtectDestroyMixin, self).perform_destroy(instance)
        except ProtectedError:
            raise exceptions.APIException('请先删除全部关联资料', 537)


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
        if isinstance(field_name, (str, unicode)):
            d = {field_name: r.data.get(field_name, default)}
            d.update(extra_params)
            rows = qset.update(**d)
        elif callable(field_name):
            rows = len(qset)
            for a in qset:
                field_name(a)
        return response.Response({'rows': rows})
