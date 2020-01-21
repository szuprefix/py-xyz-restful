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
