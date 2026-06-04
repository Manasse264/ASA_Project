from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asa', '0005_councilmember'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='councilmember',
            name='attends_council_meetings',
        ),
        migrations.RemoveField(
            model_name='councilmember',
            name='participates_in_decisions',
        ),
        migrations.RemoveField(
            model_name='councilmember',
            name='reports_reviewed',
        ),
    ]
