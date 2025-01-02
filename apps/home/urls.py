# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    # Matches any html file
    path('job/<int:job_id>', views.job_detail, name='job_detail'),
    path('graph', views.generate_graphs, name='graph'),
    #re_path(r'^.*\.*', views.pages, name='pages'),

    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
