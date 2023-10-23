from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/planetarium/", include("planetarium.urls", namespace="planetarium")),
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/user/", include("user.urls", namespace="user")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
