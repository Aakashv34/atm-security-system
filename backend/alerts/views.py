import time
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Alert
from .serializers import AlertSerializer
from .cleanup import delete_old_alerts

_last_cleanup = 0

def auto_cleanup():
    """Runs the 14-day cleanup at most once per hour."""
    global _last_cleanup
    if time.time() - _last_cleanup > 3600:
        _last_cleanup = time.time()
        delete_old_alerts()

class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer

    def get_queryset(self):
        qs = Alert.objects.all()
        if self.action == "list":
            auto_cleanup()
            p = self.request.query_params
            if p.get("label"):
                qs = qs.filter(label__icontains=p["label"])
            if p.get("camera_id"):
                qs = qs.filter(camera_id=p["camera_id"])
            if p.get("reviewed") in ("true", "false"):
                qs = qs.filter(reviewed=p["reviewed"] == "true")
            return qs[:200]
        return qs

    @action(detail=False, methods=["get"])
    def stats(self, request):
        today = timezone.localtime().date()
        first_day = today - timedelta(days=6)
        rows = (Alert.objects.filter(created_at__date__gte=first_day)
                .annotate(day=TruncDate("created_at"))
                .values("day").annotate(n=Count("id")))
        counts = {r["day"]: r["n"] for r in rows}
        days = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            days.append({"date": d.strftime("%a"), "count": counts.get(d, 0)})
        return Response({
            "total": Alert.objects.count(),
            "today": Alert.objects.filter(created_at__date=today).count(),
            "unreviewed": Alert.objects.filter(reviewed=False).count(),
            "helmet": Alert.objects.filter(label__icontains="helmet").count(),
            "mask": Alert.objects.filter(label__icontains="mask").count(),
            "days": days,
        })

    @action(detail=False, methods=["post"])
    def bulk_delete(self, request):
        qs = Alert.objects.filter(id__in=request.data.get("ids", []))
        n = qs.count()
        qs.delete()
        return Response({"deleted": n})