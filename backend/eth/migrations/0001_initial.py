# Generated by Django 4.0.2 on 2022-03-17 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Measures',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temperature', models.DecimalField(decimal_places=3, max_digits=6)),
                ('humidity', models.DecimalField(decimal_places=3, max_digits=6)),
                ('altitude', models.DecimalField(decimal_places=3, max_digits=6)),
                ('preassure', models.DecimalField(decimal_places=3, max_digits=6)),
                ('timestamp', models.DecimalField(decimal_places=3, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('station_id', models.IntegerField(primary_key=True, serialize=False)),
                ('contract_address', models.CharField(blank=True, max_length=150, null=True)),
            ],
        ),
    ]
