# Generated by Django 5.0.4 on 2024-04-13 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0002_remove_extendeduser_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='extendeduser',
            name='currency',
            field=models.CharField(choices=[('USD', 'US Dollars'), ('GBP', 'British Pounds'), ('EUR', 'Euros')], default='GBP', max_length=3),
        ),
    ]
