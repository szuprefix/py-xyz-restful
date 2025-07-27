# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals


def register(**kwargs):
    from .helper import router

    def _model_view_set_wrapper(viewset_class):
        try:
            model = viewset_class.queryset.model if viewset_class.queryset is not None else viewset_class.serializer_class.Meta.model
        except AttributeError:
            raise ValueError(f"Unable to determine model for {viewset_class}")

        mdn = getattr(model, 'alias', model._meta.model_name).lower()
        app_name = model._meta.app_label
        path = kwargs.pop('path', None) or f"{app_name}/{mdn}"

        basename = kwargs.pop('basename', f'{app_name}_{mdn}')
        # print(kwargs)
        router.register(path, viewset_class, basename=basename, **kwargs)

        return viewset_class

    return _model_view_set_wrapper


def register_raw(**kwargs):
    the_path = kwargs.pop('path', None)

    def _raw_view_set_wrapper(viewset_class):
        mod_name = viewset_class.__module__.split('.')[0]

        # 获取 app_name
        try:
            from importlib import import_module
            app_name = import_module(f'{mod_name}.apps').Config.label
        except Exception:
            app_name = mod_name

        # 构造 path 和唯一 basename
        viewset_name = viewset_class.__name__.replace('ViewSet', '').lower()
        path = the_path or f'{app_name}/{viewset_name}'
        basename = f'{app_name}_{viewset_name}'
        # print(f'basename: {basename}')

        # 导入 router
        from .helper import router

        # 检查是否已经注册
        for registered_path, registered_viewset, registered_basename in router.registry:
            if registered_basename == basename:
                # 已经注册过，不再重复注册
                return viewset_class

        # 注册
        router.register(path, viewset_class, basename=basename, **kwargs)
        return viewset_class

    return _raw_view_set_wrapper
