# Generated by Django 5.0 on 2024-01-11 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_alter_attendance_employee'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='check_in',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='check_out',
        ),
    ]
