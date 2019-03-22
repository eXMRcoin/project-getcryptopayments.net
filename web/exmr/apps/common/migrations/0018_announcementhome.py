# Generated by Django 2.0.2 on 2019-03-22 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0017_api_informationalsidebar_receivingsidebar'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnouncementHome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=2048)),
                ('visit', models.CharField(max_length=128)),
                ('link', models.URLField()),
            ],
        ),
    ]
