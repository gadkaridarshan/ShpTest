from django.urls import include, path, re_path
from . import views

urlpatterns = [
    path(r'', views.index, name='index'),
    path(r'oauth', views.oauth, name='oauth'),
    path(r'getAllCoordinates', views.getAllCoordinates, name='getAllCoordinates'),
    path(r'clearAddresses', views.clearAddresses, name='clearAddresses'),
    path(r'initRefreshToken', views.initRefreshToken, name='initRefreshToken'),
    re_path(r'^sendCoordinate/(?P<action>\w{0,50})/(?P<value>\w{0,10000})/$', views.sendCoordinate, name='sendCoordinate'),
]
