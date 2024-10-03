# Generated by Django 5.0.7 on 2024-09-07 11:01

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_reviews'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviews',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reviews',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='reviews',
            name='updated_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
