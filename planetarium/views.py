from typing import Type, List

from django.db.models import Count, F, QuerySet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from planetarium.models import (
    AstronomyShow,
    ShowTheme,
    ShowSession,
    PlanetariumDome,
    Ticket,
    Reservation,
)
from planetarium.permissions import (
    IsAdminOrIfAuthenticatedReadOnly,
    CanCreateAndRead,
)
from planetarium.serializers import (
    AstronomyShowSerializer,
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer,
    ShowThemeSerializer,
    ShowSessionSerializer,
    ShowSessionListSerializer,
    ShowSessionDetailSerializer,
    PlanetariumDomeSerializer,
    PlanetariumDomeDetailSerializer,
    PlanetariumDomeImageSerializer,
    TicketSerializer,
    TicketDetailSerializer,
    TicketListSerializer,
    ReservationSerializer,
    ReservationListSerializer,
    ReservationDetailSerializer,
)


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.prefetch_related("show_theme")
    serializer_class = AstronomyShowSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self) -> Type[AstronomyShowSerializer]:
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowDetailSerializer
        return self.serializer_class


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(qs: Type[QuerySet]) -> List[int]:
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset
        planetarium_dome = self.request.query_params.get(
            "planetarium_dome", None
        )
        astronomy_show = self.request.query_params.get("astronomy_show", None)

        if astronomy_show:
            astronomy_show_ids = self._params_to_ints(astronomy_show)
            queryset = ShowSession.objects.filter(
                astronomy_show__id__in=astronomy_show_ids
            )

        if planetarium_dome:
            planetarium_dome_ids = self._params_to_ints(planetarium_dome)
            queryset = ShowSession.objects.filter(
                planetarium_dome__id__in=planetarium_dome_ids
            )

        if self.action == "list":
            capacity = F("planetarium_dome__rows") * F(
                "planetarium_dome__seats_in_row"
            )
            queryset = queryset.select_related(
                "astronomy_show", "planetarium_dome"
            ).annotate(tickets_left=capacity - Count("tickets"))

        if self.action == "retrieve":
            queryset = queryset.select_related(
                "astronomy_show", "planetarium_dome"
            )

        return queryset.distinct()

    def get_serializer_class(self) -> Type[ShowSessionSerializer]:
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="astronomy_show",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by astronomy show id (ex. astronomy_show=1,2,3)",
            ),
            OpenApiParameter(
                name="planetarium_dome",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by planetarium dome id (ex. planetarium_dome=1,2,3)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self) -> Type[PlanetariumDomeSerializer]:
        if self.action == "retrieve":
            return PlanetariumDomeDetailSerializer
        if self.action == "upload_image":
            return PlanetariumDomeImageSerializer

        return self.serializer_class

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, *args, **kwargs) -> Response:
        """Upload an image to a planetarium dome"""
        planetarium_dome = self.get_object()
        serializer = self.get_serializer(planetarium_dome, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (CanCreateAndRead,)

    def get_queryset(self) -> QuerySet:
        queryset = Ticket.objects.filter(reservation__user=self.request.user)

        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related(
                "show_session__astronomy_show", "reservation"
            )

        return queryset

    def get_serializer_class(self) -> Type[TicketSerializer]:
        if self.action == "retrieve":
            return TicketDetailSerializer
        if self.action == "list":
            return TicketListSerializer
        return self.serializer_class

    def perform_create(self, serializer) -> None:
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
    permission_classes = (CanCreateAndRead,)

    def get_serializer_class(self) -> Type[ReservationSerializer]:
        if self.action == "list":
            return ReservationListSerializer
        if self.action == "retrieve":
            return ReservationDetailSerializer
        return self.serializer_class

    def get_queryset(self) -> QuerySet:
        queryset = Reservation.objects.filter(user=self.request.user)
        if self.action in ["list", "retrieve"]:
            queryset = queryset.prefetch_related(
                "tickets__show_session__astronomy_show",
                "tickets__show_session__planetarium_dome",
            )
        return queryset

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)
