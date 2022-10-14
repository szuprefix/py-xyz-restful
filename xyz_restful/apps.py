#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:denishuang

from __future__ import unicode_literals

from django.utils.module_loading import autodiscover_modules

from django.apps import AppConfig
from rest_framework import serializers

class Config(AppConfig):
    name = 'xyz_restful'
    label = 'restful'
    verbose_name = 'restful'

    def ready(self):
        super(Config, self).ready()
        try:
            from xyz_util import modelutils
            serializers.ModelSerializer.serializer_field_mapping.update({modelutils.JSONField: serializers.JSONField})
        except:
            import traceback
            traceback.print_exc()
        self.autodiscover()


    def autodiscover(self):
        autodiscover_modules('apis')

