from datetime import timedelta
from django.conf import settings
from rest_framework import serializers
from .models import Alert

class AlertSerializer(serializers.ModelSerializer):
    expires_at = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = "__all__"

    def get_expires_at(self, obj):
        return obj.created_at + timedelta(days=settings.RETENTION_DAYS)