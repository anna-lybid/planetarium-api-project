# Generated by Django 4.2.6 on 2023-10-23 10:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("planetarium", "0007_alter_ticket_unique_together"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="ticket",
            options={"ordering": ["row", "seat"]},
        ),
    ]