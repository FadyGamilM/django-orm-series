# Generated by Django 5.2 on 2025-04-20 22:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='resturant',
            name='causine',
            field=models.CharField(choices=[('IN', 'Indian'), ('IT', 'Italian'), ('CH', 'Chinese'), ('MX', 'Mexican'), ('AM', 'American')], default='AM', max_length=2),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stars', models.PositiveSmallIntegerField()),
                ('comment', models.TextField()),
                ('resturant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='core.resturant')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('announced', models.DateTimeField()),
                ('income', models.DecimalField(decimal_places=2, max_digits=10)),
                ('resturant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='core.resturant')),
            ],
        ),
    ]
