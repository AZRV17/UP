# Generated by Django 5.0.2 on 2024-02-18 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mag', '0003_role_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
