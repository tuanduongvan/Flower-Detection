# Generated by Django 5.1.3 on 2024-12-31 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flower_detection', '0003_alter_searchhistory_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='flower',
            name='residence',
            field=models.TextField(blank=True, null=True),
        ),
    ]