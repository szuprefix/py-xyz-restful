# -*- coding:utf-8 -*-
from collections import OrderedDict

from django.utils.encoding import force_text
from rest_framework.metadata import SimpleMetadata
from rest_framework.relations import RelatedField, SlugRelatedField, ManyRelatedField

from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework import exceptions
from rest_framework.request import clone_request
from xyz_util.modelutils import get_generic_foreign_key, get_related_field_verbose_name
from xyz_util.datautils import access

__author__ = 'denishuang'


class RelatedChoicesMetadata(SimpleMetadata):
    def determine_metadata(self, request, view):
        metadata = super(RelatedChoicesMetadata, self).determine_metadata(request, view)
        metadata['dependencies'] = self.get_dependencies(metadata)
        if hasattr(view, 'queryset'):
            model = view.queryset.model
            m = model._meta
            metadata['verbose_name'] = m.verbose_name
            if m.unique_together:
                metadata['unique_together'] = m.unique_together
            from django.contrib.contenttypes.models import ContentType
            metadata['content_type_id'] = ContentType.objects.get_for_model(model).id
            gfk = get_generic_foreign_key(m)
            if gfk:
                metadata['generic_foreign_key'] = {'name': gfk.name, 'ct_field': gfk.ct_field, 'fk_field': gfk.fk_field}
            if m.unique_together:
                metadata['unique_together'] = m.unique_together
            self.add_model_field_default_value(metadata, model)
        return metadata

    def add_model_field_default_value(self, metadata, model):
        pd = metadata.get('actions', {}).get('POST')
        if not pd:
            return
        from django.db.models.fields import NOT_PROVIDED
        for f in model._meta.get_fields():
            if f.name not in pd:
                continue
            default = getattr(f, 'default', NOT_PROVIDED)
            if default != NOT_PROVIDED:
                pd[f.name]['default'] = default

    def get_dependencies(self, metadata):
        return [
            f.get('model')
            for f in metadata.get('actions', {}).get('POST', {}).values()
            if f.get('model')
        ]

    def get_field_info(self, field):
        field_info = super(RelatedChoicesMetadata, self).get_field_info(field)
        if not field_info.get('read_only') and isinstance(field, (RelatedField, ManyRelatedField)):
            field_info = self.add_related_field_info(field, field_info)
        return field_info

    def add_related_field_info(self, field, field_info):
        if isinstance(field, ManyRelatedField):
            field = field.child_relation
            field_info['multiple'] = True
        if not hasattr(field, "queryset") or field.queryset is None:
            return field_info
        qset = field.queryset
        model = qset.model
        meta = qset.model._meta
        field_info['model'] = hasattr(model, 'alias') and meta.app_label + '.' + model.alias.lower() or meta.label_lower
        if not field.label:
            field_info['label'] = meta.verbose_name_plural
        return field_info

    def determine_actions(self, request, view):
        actions = super(RelatedChoicesMetadata, self).determine_actions(request, view)
        view.request = clone_request(request, 'GET')
        try:
            # Test global permissions
            if hasattr(view, 'check_permissions'):
                view.check_permissions(view.request)
        except (exceptions.APIException, PermissionDenied, Http404):
            pass
        else:

            search_fields = getattr(view, 'search_fields', [])
            cf = lambda f: f[0] in ['^', '@', '='] and f[1:] or f
            actions['SEARCH'] = search = {}
            search['search_fields'] = [get_related_field_verbose_name(view.queryset.model, cf(f)) for f in
                                       search_fields]
            ffs = access(view, 'filter_class._meta.fields') or getattr(view, 'filter_fields', [])
            if isinstance(ffs, dict):
                search['filter_fields'] = [{'name': k, 'lookups': v} for k, v in ffs.items()]
            else:
                search['filter_fields'] = [{'name': a, 'lookups': 'exact'} for a in ffs]
            search['ordering_fields'] = getattr(view, 'ordering_fields', [])
            serializer = view.get_serializer()
            actions['LIST'] = self.get_list_info(serializer)
        finally:
            view.request = request
        return actions

    def get_list_info(self, serializer):
        if hasattr(serializer, 'child'):
            # If this is a `ListSerializer` then we want to examine the
            # underlying child serializer instance instead.
            serializer = serializer.child
        return OrderedDict(
            [
                (field_name, self.get_list_field_info(field))
                for field_name, field in serializer.fields.items()
            ]
        )

    def get_list_field_info(self, field):
        field_info = OrderedDict()
        field_info['type'] = self.label_lookup[field]

        attrs = ['label', ]

        for attr in attrs:
            value = getattr(field, attr, None)
            if value is not None and value != '':
                field_info[attr] = force_text(value, strings_only=True)

        if getattr(field, 'child', None):
            field_info['child'] = self.get_list_field_info(field.child)
        elif getattr(field, 'fields', None):
            field_info['children'] = self.get_list_info(field)
        from rest_framework import serializers
        if isinstance(field, (serializers.RelatedField, serializers.ManyRelatedField)):
            field_info = self.add_related_field_info(field, field_info)
        elif hasattr(field, 'choices'):
            field_info['choices'] = [
                {
                    'value': choice_value,
                    'display_name': force_text(choice_name, strings_only=True)
                }
                for choice_value, choice_name in field.choices.items()
            ]

        return field_info


class RelatedSlugMetadata(SimpleMetadata):
    def get_field_info(self, field):
        field_info = super(RelatedSlugMetadata, self).get_field_info(field)

        if (not field_info.get('read_only') and
                isinstance(field, SlugRelatedField) and
                hasattr(field, 'queryset')):
            qset = field.queryset
            from django.shortcuts import reverse
            field_info['list_url'] = reverse('%s-list' % qset.model._meta.model_name)
            field_info['slug_field'] = field.slug_field
        return field_info
