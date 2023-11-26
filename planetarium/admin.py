from django.contrib import admin

from planetarium.models import (
    AstronomyShow,
    ShowTheme,
    ShowSession,
    PlanetariumDome,
    Ticket,
    Reservation,
)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)


admin.site.register(AstronomyShow)
admin.site.register(ShowTheme)
admin.site.register(ShowSession)
admin.site.register(PlanetariumDome)
admin.site.register(Ticket)
