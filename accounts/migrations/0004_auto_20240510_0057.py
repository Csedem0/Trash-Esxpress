from django.db import migrations

def create_subscription_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('accounts', 'SubscriptionPlan')
    SubscriptionPlan.objects.bulk_create([
        SubscriptionPlan(name='Basic', description='Basic subscription plan', duration_months=1, price=10.0),
        SubscriptionPlan(name='Standard', description='Standard subscription plan', duration_months=3, price=25.0),
        SubscriptionPlan(name='Premium', description='Premium subscription plan', duration_months=6, price=50.0),
    ])

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_userprofile_address'),  # Replace with the name of your previous migration
    ]

    operations = [
        migrations.RunPython(create_subscription_plans),
    ]
