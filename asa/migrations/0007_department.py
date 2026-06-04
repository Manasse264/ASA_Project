from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('asa', '0006_remove_councilmember_meeting_decision_reports'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('WELFARE', 'Welfare'), ('TEMPERANCE_FAMILY', 'Temperance and Family'), ('JA', 'J.A'), ('MIFEM', 'MIFEM'), ('CHILDREN', 'Children Department')], max_length=30, unique=True)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('leader', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='led_departments', to='asa.member')),
            ],
        ),
    ]
