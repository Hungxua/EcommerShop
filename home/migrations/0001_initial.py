# Generated by Django 2.2 on 2021-06-18 23:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'unique_together': {('title', 'slug')},
            },
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marked_price', models.PositiveIntegerField()),
                ('selling_price', models.PositiveIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Warranty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('warranty', models.CharField(blank=True, max_length=300, null=True)),
                ('return_policy', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('image', models.ImageField(upload_to='products')),
                ('description', models.TextField()),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Category')),
                ('price', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Price')),
                ('warranty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Warranty')),
            ],
        ),
    ]
