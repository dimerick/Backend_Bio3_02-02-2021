# Generated by Django 3.1.4 on 2021-01-31 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bio3', '0003_auto_20210129_0245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='location',
        ),
        migrations.AddField(
            model_name='university',
            name='tipo',
            field=models.CharField(default='university', max_length=20),
        ),
    ]
