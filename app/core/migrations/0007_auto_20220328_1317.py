# Generated by Django 2.2.14 on 2022-03-28 06:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20220328_1316'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='image1',
        ),
        migrations.RemoveField(
            model_name='item',
            name='image2',
        ),
        migrations.RemoveField(
            model_name='item',
            name='image3',
        ),
    ]
