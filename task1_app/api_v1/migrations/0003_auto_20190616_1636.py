# Generated by Django 2.2.2 on 2019-06-16 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_v1', '0002_auto_20190616_0734'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='money',
        ),
        migrations.AlterField(
            model_name='flavour',
            name='name',
            field=models.CharField(max_length=300, unique=True),
        ),
    ]
