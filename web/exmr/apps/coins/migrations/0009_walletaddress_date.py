# Generated by Django 2.0.2 on 2018-07-28 04:42

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('coins', '0008_merge_20180718_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='walletaddress',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
