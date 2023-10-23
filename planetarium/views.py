from django.db.models import Count, F
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from planetarium.models import (
    AstronomyShow,
    ShowTheme,
    ShowSession,
    PlanetariumDome,
    Ticket,
    Reservation,
)
from planetarium.serializers import (
    AstronomyShowSerializer,
    ShowThemeSerializer,
    ShowSessionSerializer,
    PlanetariumDomeSerializer,
    TicketSerializer,
    ReservationSerializer,
    TicketDetailSerializer,
    ShowSessionListSerializer,
    TicketListSerializer,
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer,
    ShowSessionDetailSerializer,
    PlanetariumDomeDetailSerializer,
    ReservationListSerializer, ReservationDetailSerializer,
)


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.prefetch_related("show_theme")
    serializer_class = AstronomyShowSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowDetailSerializer
        return self.serializer_class


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        show_session = self.request.query_params.get("show_sessions", None)
        planetarium_dome = self.request.query_params.get("planetarium_dome", None)

        if show_session:
            show_sessions_ids = self._params_to_ints(show_session)
            queryset = ShowSession.objects.filter(show_sessions__id__in=show_sessions_ids)

        if planetarium_dome:
            planetarium_dome_ids = self._params_to_ints(planetarium_dome)
            queryset = ShowSession.objects.filter(planetarium_dome__id__in=planetarium_dome_ids)

        if self.action == "list":
            capacity = F("planetarium_dome__rows") * F("planetarium_dome__seats_in_row")
            queryset = (
                queryset
                .select_related("astronomy_show", "planetarium_dome")
                .annotate(tickets_left=capacity - Count("tickets"))
            )

        if self.action == "retrieve":
            queryset = queryset.select_related("astronomy_show", "planetarium_dome")

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        return self.serializer_class


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PlanetariumDomeDetailSerializer
        return self.serializer_class


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_queryset(self):
        queryset = Ticket.objects.filter(reservation__user=self.request.user)

        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related("show_session__astronomy_show", "reservation")

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TicketDetailSerializer
        if self.action == "list":
            return TicketListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        reservation = Reservation.objects.create(user=self.request.user)
        serializer.save(reservation=reservation)


class OrderPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 100


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = OrderPagination

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        if self.action == "retrieve":
            return ReservationDetailSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = Reservation.objects.filter(user=self.request.user)
        if self.action in ["list", "retrieve"]:
            queryset = queryset.prefetch_related(
                "tickets__show_session__astronomy_show",
                "tickets__show_session__planetarium_dome"
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
