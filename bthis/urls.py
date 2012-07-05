from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bthis.views.home', name='home'),
    # url(r'^bthis/', include('bthis.foo.urls')),
    url(r'^$', 'core.views.main'),

)
