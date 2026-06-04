# Generated manually for the church council member feature.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asa', '0004_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CouncilMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('position', models.CharField(max_length=100)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('responsibilities', models.TextField(blank=True, null=True)),
                ('reports_reviewed', models.TextField(blank=True, null=True)),
                ('participates_in_decisions', models.BooleanField(default=True)),
                ('attends_council_meetings', models.BooleanField(default=True)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
