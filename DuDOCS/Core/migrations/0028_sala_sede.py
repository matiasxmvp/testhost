# Generated by Django 4.2.4 on 2023-10-17 23:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0027_remove_sala_edificio_remove_sala_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='sala',
            name='sede',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Core.sede'),
            preserve_default=False,
        ),
    ]
