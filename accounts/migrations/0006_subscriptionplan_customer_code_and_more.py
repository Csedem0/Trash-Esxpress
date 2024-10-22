# Generated by Django 4.1.13 on 2024-10-20 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_userprofile_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplan',
            name='customer_code',
            field=models.CharField(default='SUB_DEFAULT', max_length=255),
        ),
        migrations.AddField(
            model_name='usersubscription',
            name='customer_code',
            field=models.CharField(default='SUB_DEFAULT', editable=False, max_length=10, unique=True),
        ),
        migrations.AddField(
            model_name='usersubscription',
            name='pickup_code',
            field=models.CharField(default='PICKUP_DEFAULT', editable=False, max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='usersubscription',
            name='status',
            field=models.CharField(default='Active', max_length=20),
        ),
    ]
