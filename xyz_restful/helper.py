# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from rest_framework.routers import DefaultRouter


class newRouter(DefaultRouter):
    URL_PATTERNS = []

    def get_urls(self):
        urls = super(newRouter, self).get_urls()
        from .urls import urlpatterns as api_urls
        # from ..auth.urls import urlpatterns as auth_urls
        urls = api_urls + self.URL_PATTERNS + urls  # auth_urls +
        return urls

    def add_urls(self, urls):
        self.URL_PATTERNS += urls


router = newRouter()


def register(package, resource, viewset, base_name=None):
    p = "%s/%s" % (package.split(".")[-1], resource)
    router.register(p, viewset, base_name=base_name)


def register_urlpatterns(package, urls):
    from django.conf.urls import include, url
    app_name = package.split(".")[-1]
    router.add_urls([url(r'^%s/' % app_name, include(urls))])


def get_models():
    from django.apps.registry import apps
    r = {}
    for a, b, c in router.registry:
        try:
            m = apps.get_model(a.replace('/', '.'))
            r[m._meta.label_lower] = m
        except:
            pass
    return r


def get_model_viewsets():
    from django.apps.registry import apps
    r = {}
    for a, b, c in router.registry:
        try:
            mn = a.replace('/', '.')
            m = apps.get_model(mn)
            r[mn] = b
        except:
            pass
    return r


def get_model_actions():
    r = {}
    for mn, vs in get_model_viewsets().iteritems():
        r[mn] = [a for a in ['create', 'update', 'destroy'] if hasattr(vs, a)] + [a.url_path for a in
                                                                                  vs.get_extra_actions()]
    return r


def get_relation_map(reverse=False):
    d = {}
    mds = get_models()
    mdns = mds.keys()
    for n, m in mds.iteritems():
        for f in m._meta.get_fields():
            if not f.is_relation or f.many_to_one:
                continue
            m2 = f.related_model
            if not m2 and f.ct_field:
                for n2 in mdns:
                    if n2 != n:
                        k = n2 if reverse == True else n
                        v = n if reverse == True else n2
                        d.setdefault(k, {}).setdefault(v, []).append((f, m, 'gfk'))
            else:
                n2 = m2._meta.label_lower
                if n2 in mdns:
                    k = n2 if reverse == True else n
                    v = n if reverse == True else n2
                    d.setdefault(k, {}).setdefault(v, []).append((f, m, m2))
    return d


def get_user_resources():
    start_point = 'auth.user'
    mm = get_relation_map()
    a = mm.get(start_point)
    d = {}
    dp = {}
    for k, v in a.iteritems():
        d.setdefault(k, [])
        for r in v:
            fp = r[0].name
            d[k].append(fp)
            dp[fp] = [r[1], r[2]]

    def gen_paths():
        cnt = 0
        for dk, dv in d.items():
            a = mm.get(dk)
            if not a:
                continue
            for k, v in a.iteritems():
                if k == start_point:
                    continue
                d.setdefault(k, [])
                for r in v:
                    for p in dv:
                        fp = p + '.' + r[0].name
                        if fp not in d[k] and r[2] not in dp[p]:
                            d[k].append(fp)
                            dp[fp] = dp[p] + [r[2]]
                            cnt += 1
        return cnt

    while gen_paths() > 0:
        pass
    for dk, dv in d.items():
        d[dk] = sorted(dv)
    return d
