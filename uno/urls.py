from django.conf.urls import url,include
from django.contrib.auth import views as auth_views
from allauth.account import views as all_views
from . import views

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'uno/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'uno/logout.html'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'oauth/', include('allauth.urls')),
    
    
    url(r'^lobby/$', views.lobby, name='lobby'),
    url(r'^games$', views.get_lobby_games, name='games'),
    url(r'^game/(?P<game_id>\d+)/join$', views.join, name='join'),
    url(r'^game/(?P<game_id>\d+)/delete$', views.delete, name='delete'),
    url(r'^game/(?P<game_id>\d+)/start$', views.start, name='start'),
    url(r'^game/(?P<game_id>\d+)/play$', views.play, name='play'),
    url(r'^$', views.index, name='index' ),
]
