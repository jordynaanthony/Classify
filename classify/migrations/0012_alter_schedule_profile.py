# Generated by Django 4.0.2 on 2022-11-02 21:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classify', '0011_schedule_name_alter_schedule_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='classify.profile'),
        ),
    ]