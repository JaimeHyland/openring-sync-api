from django.db import models


class Device(models.Model):
    STATUS_REGISTERED = "registered"
    STATUS_ACTIVE = "active"
    STATUS_ERROR = "error"

    STATUS_CHOICES = [
        (STATUS_REGISTERED, "Registered"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_ERROR, "Error"),
    ]

    device_id = models.CharField(max_length=100, unique=True)
    firmware_version = models.CharField(max_length=50)
    hardware_revision = models.CharField(max_length=50)
    supported_sensor_modules = models.JSONField(default=list)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_REGISTERED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.device_id


class StudySession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    study_name = models.CharField(max_length=255)
    anonymized_participant_id = models.CharField(max_length=100)
    assigned_device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="study_sessions",
    )
    enabled_sensor_modules = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.session_id


class SensorBatch(models.Model):
    batch_id = models.CharField(max_length=100)
    device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="sensor_batches",
    )
    session = models.ForeignKey(
        StudySession,
        on_delete=models.PROTECT,
        related_name="sensor_batches",
    )
    sensor_type = models.CharField(max_length=50)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["device", "batch_id"],
                name="unique_batch_per_device",
            )
        ]

    def __str__(self):
        return f"{self.device.device_id} - {self.batch_id}"


class SensorReading(models.Model):
    batch = models.ForeignKey(
        SensorBatch,
        on_delete=models.CASCADE,
        related_name="readings",
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="sensor_readings",
    )
    session = models.ForeignKey(
        StudySession,
        on_delete=models.PROTECT,
        related_name="sensor_readings",
    )
    sensor_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    sequence_number = models.PositiveIntegerField(null=True, blank=True)
    values = models.JSONField()
    quality_flags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["session", "sensor_type", "timestamp"]),
            models.Index(fields=["device", "sensor_type", "timestamp"]),
        ]
        ordering = ["session", "sensor_type", "timestamp"]

    def __str__(self):
        return f"{self.session.session_id} - {self.sensor_type} - {self.timestamp}"
    