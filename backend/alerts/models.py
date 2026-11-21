from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Alert(models.Model):
    camera_id = models.CharField(max_length=50, default="ATM-1")
    label = models.CharField(max_length=100)
    confidence = models.FloatField(default=0)
    snapshot = models.ImageField(upload_to="snapshots/")
    reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

@receiver(post_delete, sender=Alert)
def delete_snapshot_file(sender, instance, **kwargs):
    # remove the image file from disk when the alert is deleted
    if instance.snapshot:
        instance.snapshot.delete(save=False)