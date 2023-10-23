from django.contrib.auth.models import AbstractUser
from django.db import models

from planetarium_api import settings


class AstronomyShow(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    show_theme = models.ManyToManyField("ShowTheme", related_name="astronomy_shows")

    def __str__(self):
        return self.title


class ShowTheme(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(AstronomyShow, on_delete=models.CASCADE, related_name="sessions")
    planetarium_dome = models.ForeignKey("PlanetariumDome", on_delete=models.CASCADE, related_name="sessions")
    show_time = models.DateTimeField()

    def __str__(self):
        return f"{self.astronomy_show.title} - {self.planetarium_dome.name} - {self.show_time}"


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=100, unique=True)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    show_session = models.ForeignKey(ShowSession, on_delete=models.CASCADE, related_name="tickets")
    reservation = models.ForeignKey("Reservation", on_delete=models.CASCADE, related_name="tickets", null=False)

    def __str__(self):
        return f"row: {self.row} - seat: {self.seat}. Show: {self.show_session.astronomy_show.title}"

    class Meta:
        unique_together = ("row", "seat", "show_session")


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")

    def __str__(self):
        return str(self.user)

    class Meta:
        ordering = ["-created_at"]
