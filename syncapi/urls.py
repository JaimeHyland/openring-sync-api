from django.urls import path

from .views import (
    DeviceCreateView,
    DeviceDetailView,
    SensorBatchIngestView,
    SessionReadingsView,
    StudySessionCreateView,
    StudySessionDetailView,
)

urlpatterns = [
    path("devices/", DeviceCreateView.as_view(), name="device-create"),
    path("devices/<str:device_id>/", DeviceDetailView.as_view(), name="device-detail"),
    path("sessions/", StudySessionCreateView.as_view(), name="session-create"),
    path(
        "sessions/<str:session_id>/",
        StudySessionDetailView.as_view(),
        name="session-detail",
    ),
    path("sync/batches/", SensorBatchIngestView.as_view(), name="sync-batch-ingest"),
    path(
        "sessions/<str:session_id>/readings/",
        SessionReadingsView.as_view(),
        name="session-readings",
    ),
]
