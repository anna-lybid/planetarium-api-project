# Generated by Django 4.2.6 on 2023-10-20 10:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("planetarium", "0004_alter_reservation_options"),
    ]

    operations = [
        migrations.DeleteModel(
            name="User",
        ),
    ]
