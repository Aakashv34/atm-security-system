from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from .models import Alert

def delete_old_alerts():
    cutoff = timezone.now() - timedelta(days=settings.RETENTION_DAYS)
    old = Alert.objects.filter(created_at__lt=cutoff)
    count = old.count()
    old.delete()
    return count