# Generated by Django 2.0.2 on 2018-07-10 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchant_tools', '0007_urlmaker_url_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='urlmaker',
            name='unique_id',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
