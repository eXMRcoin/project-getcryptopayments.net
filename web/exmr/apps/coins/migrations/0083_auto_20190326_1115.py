# Generated by Django 2.0.2 on 2019-03-26 11:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coins', '0082_auto_20190325_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coins.Coin'),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='token_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coins.EthereumToken'),
        ),
    ]
