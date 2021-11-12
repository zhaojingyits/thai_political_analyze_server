"""tweet_showing_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from . import get_user,show_trends_page,get_summary_from_summary_table,get_nextpage,get_search
urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^user$', get_user.dump),
    url(r'^trend$', show_trends_page.dump),
    url(r'^summary$', get_summary_from_summary_table.dump),
    url(r'^nextpage$', get_nextpage.dump),
    url(r'^search$', get_search.dump),
]
