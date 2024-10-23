# Generated by Django 4.1.13 on 2024-10-23 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersubscription',
            name='current_pickup_code',
        ),
        migrations.RemoveField(
            model_name='usersubscription',
            name='pickup_codes',
        ),
        migrations.AddField(
            model_name='usersubscription',
            name='pickup_code',
            field=models.CharField(default='PICKUP_DEFAULT', editable=False, max_length=10, unique=True),
        ),
    ]
