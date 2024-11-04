# Generated by Django 5.1.2 on 2024-10-31 14:05

import django.contrib.auth.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "price",
                    models.DecimalField(decimal_places=2, default=0, max_digits=6),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("email", models.EmailField(max_length=100)),
                (
                    "date_modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name=django.contrib.auth.models.User
                    ),
                ),
                ("address1", models.CharField(blank=True, max_length=200)),
                ("address2", models.CharField(blank=True, max_length=200)),
                ("city", models.CharField(blank=True, max_length=200)),
                ("region", models.CharField(blank=True, max_length=200)),
                ("postcode", models.CharField(blank=True, max_length=20)),
                ("country", models.CharField(blank=True, max_length=200)),
                ("old_cart", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
