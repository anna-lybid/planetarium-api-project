from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/planetarium/", include("planetarium.urls", namespace="planetarium")),
    path("__debug__/", include("debug_toolbar.urls")),
]
