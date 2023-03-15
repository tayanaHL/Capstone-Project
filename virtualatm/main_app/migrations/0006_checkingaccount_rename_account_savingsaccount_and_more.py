# Generated by Django 4.1.7 on 2023-03-15 02:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_user_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckingAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, max_digits=8)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RenameModel(
            old_name='Account',
            new_name='SavingsAccount',
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.RenameField(
            model_name='savingsaccount',
            old_name='account_type',
            new_name='account_number',
        ),
        migrations.AlterField(
            model_name='savingsaccount',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
