# Generated by Django 5.0.6 on 2024-09-26 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_appointment_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='fee',
            field=models.IntegerField(default=1000),
        ),
    ]
