from django.db import models


class DeviceSyncState(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    last_accepted_sequence = models.PositiveIntegerField(null=True, blank=True)
    last_successful_sync_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device_id} - last sequence: {self.last_accepted_sequence}"


class SensorReading(models.Model):
    device_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100, blank=True)

    sequence = models.PositiveIntegerField()
    timestamp = models.DateTimeField()

    temperature_c = models.FloatField(null=True, blank=True)
    heart_rate_bpm = models.PositiveIntegerField(null=True, blank=True)
    spo2_percent = models.PositiveIntegerField(null=True, blank=True)

    motion = models.JSONField(null=True, blank=True)

    sync_request_id = models.CharField(max_length=100, blank=True)
    batch_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("device_id", "sequence")
        ordering = ["device_id", "sequence"]

    def __str__(self):
        return f"{self.device_id} #{self.sequence}"