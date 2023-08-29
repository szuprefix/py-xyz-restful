# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from django.dispatch import Signal

batch_action_post = Signal(providing_args=["queryset", "field_name", "default"])

