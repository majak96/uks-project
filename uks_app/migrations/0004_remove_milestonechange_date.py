# Generated by Django 3.0.2 on 2020-02-02 12:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uks_app', '0003_auto_20200202_1325'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='milestonechange',
            name='date',
        ),
    ]