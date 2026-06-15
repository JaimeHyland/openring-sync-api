from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiResponse, extend_schema

from .models import Device, StudySession, SensorReading
from .serializers import (
    DeviceSerializer,
    SensorBatchIngestSerializer,
    SensorReadingSerializer,
    StudySessionSerializer,
    BatchIngestResponseSerializer,
)


class DeviceCreateView(generics.CreateAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class DeviceDetailView(generics.RetrieveAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    lookup_field = "device_id"


class StudySessionCreateView(generics.CreateAPIView):
    queryset = StudySession.objects.all()
    serializer_class = StudySessionSerializer


class StudySessionDetailView(generics.RetrieveAPIView):
    queryset = StudySession.objects.all()
    serializer_class = StudySessionSerializer
    lookup_field = "session_id"


class SensorBatchIngestView(APIView):
    serializer_class = SensorBatchIngestSerializer

    @extend_schema(
        request=SensorBatchIngestSerializer,
        responses={
            201: BatchIngestResponseSerializer,
            200: BatchIngestResponseSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
    )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        response_status = (
            status.HTTP_201_CREATED
            if result["status"] == "ingested"
            else status.HTTP_200_OK
        )

        return Response(result, status=response_status)


class SessionReadingsView(generics.ListAPIView):
    serializer_class = SensorReadingSerializer

    def get_queryset(self):
        session_id = self.kwargs["session_id"]
        return SensorReading.objects.filter(
            session__session_id=session_id,
        ).order_by("timestamp", "sequence_number")