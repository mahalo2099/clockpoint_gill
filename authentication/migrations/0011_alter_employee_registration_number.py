# Generated by Django 5.0 on 2024-01-11 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_attendance_check_in_attendance_check_out'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='registration_number',
            field=models.CharField(max_length=100),
        ),
    ]
