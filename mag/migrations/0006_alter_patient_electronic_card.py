# Generated by Django 5.0.2 on 2024-02-20 06:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mag', '0005_alter_record_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='electronic_card',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mag.electroniccard'),
        ),
    ]
