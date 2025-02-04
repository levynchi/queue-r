from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile

class Command(BaseCommand):
    help = 'Clean up orphaned Profile records'

    def handle(self, *args, **kwargs):
        orphaned_profiles = Profile.objects.filter(user__isnull=True)
        count = orphaned_profiles.count()
        orphaned_profiles.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} orphaned Profile records'))