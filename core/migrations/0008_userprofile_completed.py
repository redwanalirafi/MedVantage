# Generated by Django 5.0.6 on 2024-09-12 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_appointment_fee_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]
