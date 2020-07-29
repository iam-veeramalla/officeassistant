"""SiteManagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, patterns, include
from django.contrib import admin
from django.contrib.auth import views as auth_views

from core.views import MainView
from core.views import RequestsView, RequestView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
                       url(r'^admin/', admin.site.urls),
                       url(r'^play/$', MainView.as_view()),
                       url(r'^$', auth_views.login, {'template_name': 'login.html'}, name='login'),
                       url(r'login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
                       url(r'^registration$', 'core.views.registration', name='registration'),
                       url(r'dashboard$', 'core.views.dashboard', name='dashboard'),
                       url(r'requests$', RequestsView.as_view(), name="requests"),
                       url('request/(?P<pk>[0-9]+)/$', RequestView.as_view(), name='request_detail'),
                       url(r'create_request', 'core.views.createRequest', name='create_request'),
                       url(r'update_request', 'core.views.updateRequest', name='update_request'),
                       url(r'set_limit', 'core.views.set_limit', name='set_limit'),
                       url(r'quotarequest', 'core.views.quotarequest', name='quotarequest'),
                       url(r'donatequota', 'core.views.donatequota', name='donatequota'),
                       url(r'quotastore', 'core.views.quotastore', name='quotastore'),
                       url(r'logout', auth_views.login, {'template_name': 'logout.html'}, name='logout'),
                       url('^', include('django.contrib.auth.urls')),
                       ) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)