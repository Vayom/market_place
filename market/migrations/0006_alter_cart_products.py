# Generated by Django 5.0.4 on 2024-04-19 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0005_alter_order_status_alter_userprofile_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='products',
            field=models.ManyToManyField(blank=True, null=True, to='market.product'),
        ),
    ]
