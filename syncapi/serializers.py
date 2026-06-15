from django.db import IntegrityError, transaction
from rest_framework import serializers

from .models import Device, StudySession, SensorBatch, SensorReading


class DeviceSerializer(serializers.ModelSerializer):
    supported_sensor_modules = serializers.ListField(
        child=serializers.CharField(),
    )

    class Meta:
        model = Device
        fields = [
            "device_id",
            "firmware_version",
            "hardware_revision",
            "supported_sensor_modules",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class StudySessionSerializer(serializers.ModelSerializer):
    assigned_device_id = serializers.CharField(write_only=True)
    assigned_device = DeviceSerializer(read_only=True)
    enabled_sensor_modules = serializers.ListField(
        child=serializers.CharField(),
    )

    class Meta:
        model = StudySession
        fields = [
            "session_id",
            "study_name",
            "anonymized_participant_id",
            "assigned_device_id",
            "assigned_device",
            "enabled_sensor_modules",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["assigned_device", "created_at", "updated_at"]

    def validate_assigned_device_id(self, value):
        if not Device.objects.filter(device_id=value).exists():
            raise serializers.ValidationError(f"Unknown device_id '{value}'.")
        return value

    def create(self, validated_data):
        assigned_device_id = validated_data.pop("assigned_device_id")
        device = Device.objects.get(device_id=assigned_device_id)
        return StudySession.objects.create(
            assigned_device=device,
            **validated_data,
        )

class SensorReadingSerializer(serializers.ModelSerializer):
    values = serializers.JSONField()
    quality_flags = serializers.ListField(
        child=serializers.CharField(),
    )

    class Meta:
        model = SensorReading
        fields = [
            "sensor_type",
            "timestamp",
            "sequence_number",
            "values",
            "quality_flags",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class ReadingInputSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    sequence_number = serializers.IntegerField(required=False, min_value=0)
    values = serializers.JSONField()
    quality_flags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )

    def validate_values(self, value):
        if not isinstance(value, dict) or not value:
            raise serializers.ValidationError("values must be a non-empty JSON object.")
        return value


class SensorBatchIngestSerializer(serializers.Serializer):
    batch_id = serializers.CharField(max_length=100)
    device_id = serializers.CharField(max_length=100)
    session_id = serializers.CharField(max_length=100)
    sensor_type = serializers.CharField(max_length=50)
    readings = ReadingInputSerializer(many=True)

    def validate(self, attrs):
        device_id = attrs["device_id"]
        session_id = attrs["session_id"]
        sensor_type = attrs["sensor_type"]

        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            raise serializers.ValidationError(
                {"device_id": f"Unknown device_id '{device_id}'."}
            )

        try:
            session = StudySession.objects.get(session_id=session_id)
        except StudySession.DoesNotExist:
            raise serializers.ValidationError(
                {"session_id": f"Unknown session_id '{session_id}'."}
            )

        if session.assigned_device_id != device.id:
            raise serializers.ValidationError(
                "Device is not assigned to this study session."
            )

        if sensor_type not in device.supported_sensor_modules:
            raise serializers.ValidationError(
                {"sensor_type": f"Sensor type '{sensor_type}' is not supported by this device."}
            )

        if sensor_type not in session.enabled_sensor_modules:
            raise serializers.ValidationError(
                {"sensor_type": f"Sensor type '{sensor_type}' is not enabled for this session."}
            )

        attrs["device"] = device
        attrs["session"] = session
        return attrs

    def save(self):
        batch_id = self.validated_data["batch_id"]
        device = self.validated_data["device"]
        session = self.validated_data["session"]
        sensor_type = self.validated_data["sensor_type"]
        readings = self.validated_data["readings"]

        existing_batch = SensorBatch.objects.filter(
            device=device,
            batch_id=batch_id,
        ).first()

        if existing_batch:
            return {
                "status": "duplicate",
                "batch_id": batch_id,
                "readings_ingested": 0,
            }

        try:
            with transaction.atomic():
                batch = SensorBatch.objects.create(
                    batch_id=batch_id,
                    device=device,
                    session=session,
                    sensor_type=sensor_type,
                )

                reading_objects = [
                    SensorReading(
                        batch=batch,
                        device=device,
                        session=session,
                        sensor_type=sensor_type,
                        timestamp=reading["timestamp"],
                        sequence_number=reading.get("sequence_number"),
                        values=reading["values"],
                        quality_flags=reading.get("quality_flags", []),
                    )
                    for reading in readings
                ]

                SensorReading.objects.bulk_create(reading_objects)

        except IntegrityError:
            return {
                "status": "duplicate",
                "batch_id": batch_id,
                "readings_ingested": 0,
            }

        return {
            "status": "ingested",
            "batch_id": batch_id,
            "readings_ingested": len(readings),
        }
    
class BatchIngestResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    batch_id = serializers.CharField()
    readings_ingested = serializers.IntegerField()
    