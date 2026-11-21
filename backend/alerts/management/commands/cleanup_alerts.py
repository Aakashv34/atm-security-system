from django.core.management.base import BaseCommand
from alerts.cleanup import delete_old_alerts

class Command(BaseCommand):
    help = "Delete alerts older than RETENTION_DAYS"

    def handle(self, *args, **options):
        n = delete_old_alerts()
        self.stdout.write(f"Deleted {n} old alerts")