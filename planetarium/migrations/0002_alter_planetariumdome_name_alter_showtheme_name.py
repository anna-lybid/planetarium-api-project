# Generated by Django 4.2.6 on 2023-10-20 10:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("planetarium", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="planetariumdome",
            name="name",
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name="showtheme",
            name="name",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]