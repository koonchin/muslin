# Generated by Django 2.2.14 on 2022-03-28 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20220328_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='test_foreign',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
