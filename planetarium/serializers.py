from rest_framework import serializers

from planetarium.models import AstronomyShow, ShowTheme, ShowSession, PlanetariumDome, Ticket, Reservation


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "show_theme")


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time")


class ShowSessionListSerializer(ShowSessionSerializer):
    planetarium_dome = serializers.StringRelatedField(many=False, read_only=True)
    astronomy_show = serializers.SlugRelatedField(many=False, read_only=True, slug_field="title")
    tickets_left = serializers.IntegerField(read_only=True)
    tickets_sold = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time", "tickets_sold", "tickets_left")


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    show_session = ShowSessionSerializer(read_only=True)
    reservation = ReservationSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session", "reservation")


class TicketDetailSerializer(TicketSerializer):
    show_session = ShowSessionListSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session", "reservation")


