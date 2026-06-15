from django.contrib import admin
from .models import Device, StudySession, SensorBatch, SensorReading


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "device_id",
        "firmware_version",
        "hardware_revision",
        "status",
        "created_at",
    )
    search_fields = ("device_id",)
    list_filter = ("status",)


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = (
        "session_id",
        "study_name",
        "anonymized_participant_id",
        "assigned_device",
        "created_at",
    )
    search_fields = (
        "session_id",
        "study_name",
        "anonymized_participant_id",
        "assigned_device__device_id",
    )
    list_filter = ("study_name",)


@admin.register(SensorBatch)
class SensorBatchAdmin(admin.ModelAdmin):
    list_display = (
        "batch_id",
        "device",
        "session",
        "sensor_type",
        "received_at",
    )
    search_fields = (
        "batch_id",
        "device__device_id",
        "session__session_id",
        "sensor_type",
    )
    list_filter = ("sensor_type",)
    ordering = ("-received_at",)


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "device",
        "sensor_type",
        "timestamp",
        "sequence_number",
        "created_at",
    )
    search_fields = (
        "session__session_id",
        "device__device_id",
        "sensor_type",
    )
    list_filter = (
        "sensor_type",
        "session",
        "device",
    )
    ordering = ("-timestamp", "sequence_number")
