from django.contrib import admin

from .models import DeviceSyncState, SensorReading


@admin.register(DeviceSyncState)
class DeviceSyncStateAdmin(admin.ModelAdmin):
    list_display = (
        "device_id",
        "last_accepted_sequence",
        "last_successful_sync_at",
        "created_at",
        "updated_at",
    )
    search_fields = ("device_id",)
    ordering = ("device_id",)


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = (
        "device_id",
        "user_id",
        "sequence",
        "timestamp",
        "temperature_c",
        "heart_rate_bpm",
        "spo2_percent",
        "batch_id",
        "created_at",
    )
    list_filter = (
        "device_id",
        "user_id",
        "batch_id",
        "created_at",
    )
    search_fields = (
        "device_id",
        "user_id",
        "sync_request_id",
        "batch_id",
    )
    ordering = ("device_id", "sequence")
    readonly_fields = ("created_at",)