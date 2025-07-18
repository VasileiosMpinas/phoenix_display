# Generated by Django 4.2.7 on 2023-12-09 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_page', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('video_file', models.FileField(upload_to='videos/')),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
