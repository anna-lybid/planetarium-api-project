from django.urls import path, include
from rest_framework import routers

from planetarium.views import (
    AstronomyShowViewSet,
    ShowThemeViewSet,
    ShowSessionViewSet,
    PlanetariumDomeViewSet,
    TicketViewSet,
    ReservationViewSet,
)

router = routers.DefaultRouter()
router.register("astronomy_shows", AstronomyShowViewSet)
router.register("show_themes", ShowThemeViewSet)
router.register("show_sessions", ShowSessionViewSet)
router.register("planetarium_domes", PlanetariumDomeViewSet)
router.register("tickets", TicketViewSet)
router.register("reservations", ReservationViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "planetarium"
