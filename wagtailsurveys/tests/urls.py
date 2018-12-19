from django.conf.urls import include, url
try:
    from wagtail.core import urls as wagtail_urls
    from wagtail.admin import urls as wagtailadmin_urls
except ImportError:  # fallback for Wagtail <2.0
    from wagtail.wagtailcore import urls as wagtail_urls
    from wagtail.wagtailadmin import urls as wagtailadmin_urls

urlpatterns = [
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'', include(wagtail_urls)),
]
