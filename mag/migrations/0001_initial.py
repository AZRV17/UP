# Generated by Django 5.0.2 on 2024-02-18 07:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('surname', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=50)),
                ('direction', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ElectronicCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medical_card', models.CharField(max_length=50)),
                ('result', models.CharField(max_length=50)),
                ('diagnosis', models.CharField(max_length=50)),
                ('treatment', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('treatment', models.CharField(max_length=50)),
                ('denomination', models.CharField(max_length=50)),
                ('deadline', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schedule', models.CharField(max_length=50)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mag.doctor')),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('surname', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=50)),
                ('phone_number', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
                ('electronic_card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mag.electroniccard')),
                ('role', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mag.role')),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calendar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mag.calendar')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mag.patient')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mag.recipe')),
            ],
        ),
        migrations.AddField(
            model_name='doctor',
            name='role',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mag.role'),
        ),
    ]