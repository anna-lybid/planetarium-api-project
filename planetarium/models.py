from django.contrib.auth.models import AbstractUser
from django.db import models

from planetarium_api import settings


class AstronomyShow(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


class ShowTheme(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(AstronomyShow, on_delete=models.CASCADE, related_name="sessions")
    planetarium_dome = models.ForeignKey("PlanetariumDome", on_delete=models.CASCADE, related_name="sessions")
    show_time = models.DateTimeField()

    def __str__(self):
        return f"{self.astronomy_show.title} - {self.planetarium_dome.name} - {self.show_time}"


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    show_session = models.ForeignKey(ShowSession, on_delete=models.CASCADE, related_name="tickets")
    reservation = models.ForeignKey("Reservation", on_delete=models.CASCADE, related_name="tickets", null=True)

    def __str__(self):
        return f"{self.row} - {self.seat} - {self.show_session}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")

    def __str__(self):
        return f"{self.user} - {self.created_at}"


class User(AbstractUser):
    pass
