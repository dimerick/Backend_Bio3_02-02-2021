# Generated by Django 3.1.4 on 2021-01-31 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bio3', '0004_auto_20210131_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='university',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]
