# Generated by Django 4.0.1 on 2022-04-05 08:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reply',
            name='post',
        ),
        migrations.RemoveField(
            model_name='reply',
            name='user',
        ),
        migrations.DeleteModel(
            name='Post',
        ),
        migrations.DeleteModel(
            name='Reply',
        ),
    ]
