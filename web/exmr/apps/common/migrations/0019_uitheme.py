# Generated by Django 2.0.2 on 2019-04-03 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0018_announcementhome'),
    ]

    operations = [
        migrations.CreateModel(
            name='UITheme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme_name', models.CharField(max_length=128)),
                ('file_name', models.CharField(max_length=128)),
            ],
        ),
    ]
