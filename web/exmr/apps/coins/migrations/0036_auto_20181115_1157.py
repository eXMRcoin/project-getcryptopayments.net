# Generated by Django 2.0.2 on 2018-11-15 11:57

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('coins', '0035_auto_20181115_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paybyname',
            name='expiry',
            field=models.DateTimeField(default=datetime.datetime(2018, 12, 15, 11, 57, 48, 550617, tzinfo=utc)),
        ),
    ]