# Open Ring Sync API

This littel project is a backend-only Django REST Framework prototype for batched smart-ring sensor data synchronization.

This project was built for a timed technical assessment. It demonstrates how a backend API could register wearable devices, create research study sessions, ingest batches of sensor readings from a simulated sync client, validate incoming data, prevent duplicate ingestion, and expose readings for retrieval or export.

There is no frontend, no real BLE implementation, and no direct communication between the backend and the ring.

## What this demonstrates

* device registration
* study session creation
* batched sensor-data ingestion
* validation of device, session, and sensor consistency
* duplicate batch handling using `batch_id`
* retrieval/export of readings for a session
* automated API tests for the core success and failure paths
* documented assumptions, limitations, and production next steps

## Assessment approach

I treated this as a timed MVP exercise rather than an attempt to build a complete wearable research platform.

My priority was to demonstrate the core backend sync/data-integrity path:

1. register a device
2. create a study session
3. receive a batch of readings from a simulated sync client
4. validate the payload against known devices, sessions, and enabled sensors
5. reject inconsistent or malformed input
6. avoid duplicate ingestion
7. retrieve/export readings for a session

I intentionally did not implement a frontend dashboard, real BLE communication, authentication, deployment infrastructure, real-time streaming, or large-scale sensor storage. These are important production concerns, but I considered them secondary to proving the core ingestion workflow for this assessment.

## Architecture assumption

The smart ring does not communicate directly with the backend.

The assumed flow is:

```text
Smart ring firmware
  ↓ BLE
Mobile/Desktop sync client
  ↓ HTTPS JSON batch
Django REST backend
  ↓
Database
  ↓
Researcher dashboard/export
```

The mobile or desktop sync client is responsible for BLE communication, local device reads, binary decoding, retry behavior, and packaging readings into JSON batches.

The backend receives normalized JSON batches and treats them as untrusted input. It validates device IDs, session IDs, sensor types, timestamps, duplicate batch IDs, and payload structure before storing readings.

More detail is in [`docs/architecture.md`](docs/architecture.md).

## Tech stack

* Python
* Django
* Django REST Framework
* SQLite for local development
* drf-spectacular for OpenAPI/Swagger documentation
* pytest / Django tests for automated API coverage

I chose Django and Django REST Framework because they provide clear data modelling, validation, persistence, API structure, and test support while remaining familiar and production-oriented.

SQLite keeps the assessment lightweight and easy to run locally. In production, I would expect this to move to PostgreSQL with stronger constraints, indexing, and background processing for heavier ingestion and export workloads.

## API endpoints

Planned/core endpoints:

```http
POST /api/devices/
GET  /api/devices/{device_id}/

POST /api/sessions/
GET  /api/sessions/{session_id}/

POST /api/sync/batches/
GET  /api/sessions/{session_id}/readings/
GET  /api/sessions/{session_id}/export/
```

The most important endpoint is:

```http
POST /api/sync/batches/
```

This endpoint receives sensor readings from the simulated sync client.

## Example device registration

```http
POST /api/devices/
```

```json
{
  "device_id": "ring-001",
  "firmware_version": "1.0.3",
  "hardware_revision": "rev-a",
  "supported_sensor_modules": ["imu", "ppg", "temperature"],
  "status": "registered"
}
```

## Example study session creation

```http
POST /api/sessions/
```

```json
{
  "session_id": "session-001",
  "study_name": "Sleep Recovery Pilot",
  "anonymized_participant_id": "participant-001",
  "assigned_device_id": "ring-001",
  "enabled_sensor_modules": ["imu", "ppg", "temperature"]
}
```

## Example sync batch upload

```http
POST /api/sync/batches/
```

```json
{
  "batch_id": "batch-20260101-ring-001-imu-0001",
  "device_id": "ring-001",
  "session_id": "session-001",
  "sensor_type": "imu",
  "readings": [
    {
      "timestamp": "2026-01-01T12:00:00.000Z",
      "sequence_number": 1001,
      "values": {
        "accel_x": 0.01,
        "accel_y": 0.02,
        "accel_z": 0.98,
        "gyro_x": 0.001,
        "gyro_y": 0.002,
        "gyro_z": 0.003
      },
      "quality_flags": []
    }
  ]
}
```

Example accepted response:

```json
{
  "status": "ingested",
  "batch_id": "batch-20260101-ring-001-imu-0001",
  "readings_ingested": 1
}
```

Example duplicate response:

```json
{
  "status": "duplicate",
  "batch_id": "batch-20260101-ring-001-imu-0001",
  "readings_ingested": 0
}
```

## Validation rules

The sync batch endpoint validates that:

* the request body is valid JSON
* required fields are present
* the device exists
* the session exists
* the batch device matches the session's assigned device
* the sensor type is supported by the device
* the sensor type is enabled for the session
* the batch has not already been ingested
* readings contain valid timestamps and JSON values

The API rejects:

* unknown devices
* unknown sessions
* batches for a device not assigned to the session
* unsupported sensor types
* disabled sensor types
* malformed reading payloads
* duplicate batch submissions

## Idempotency

The sync client may retry a batch if the network fails or if it does not receive a response from the backend. Without duplicate handling, a retry could create duplicate readings.

This prototype uses `batch_id` to make ingestion idempotent. If a batch has already been accepted, a repeated submission returns a duplicate response and does not create new readings.

In production, this should be enforced with a database uniqueness constraint such as:

```text
device + batch_id
```

## Missing data

The MVP primarily prevents duplicate batch ingestion. It does not fully reconstruct or repair missing data.

Optional `sequence_number` values provide a basis for detecting gaps, out-of-order readings, or partial sync failures later. For example, if a session contains readings with sequence numbers `1001`, `1002`, and `1004`, the platform can flag that sequence `1003` may be missing.

## API documentation

Swagger UI is available locally at:

```text
http://127.0.0.1:8000/api/docs/
```

The raw OpenAPI schema is available at:

```text
http://127.0.0.1:8000/api/schema/
```

## Local setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Or, during initial setup:

```powershell
pip install django djangorestframework django-cors-headers drf-spectacular python-dotenv pytest pytest-django
pip freeze > requirements.txt
```

Run migrations:

```powershell
python manage.py migrate
```

Start the development server:

```powershell
python manage.py runserver
```

Open Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

## Running tests

```powershell
pytest
```

or, if using Django's built-in test runner:

```powershell
python manage.py test
```

Automated tests cover, or are intended to cover:

* device registration
* session creation
* valid batch ingestion
* duplicate batch handling
* unknown device rejection
* unknown session rejection
* device/session mismatch rejection
* disabled sensor rejection
* unsupported sensor rejection
* malformed payload validation
* retrieval of readings for a session

## Project status

Implemented:

* Django project setup
* Django REST Framework installed
* OpenAPI / Swagger UI configured
* initial backend models
* core API endpoints
* initial validation and duplicate handling
* initial tests

Planned or incomplete:

* further test coverage
* richer OpenAPI examples
* CSV export, if not implemented
* authentication and authorization
* production audit logging
* async export jobs
* dashboard aggregation
* stronger sync protocol with firmware/mobile teams

## Documentation

* [`docs/architecture.md`](docs/architecture.md) — MVP architecture, data model, sync boundary, security/privacy, scaling path, risks and unknowns
* [`docs/debugging-investigation.md`](docs/debugging-investigation.md) — investigation approach for the three debugging scenarios
* [`docs/resources.md`](docs/resources.md) — tools, AI usage, and external resources consulted

## Tools used

* IDE: Visual Studio Code
* Backend: Python, Django, Django REST Framework
* Database: SQLite
* API documentation: drf-spectacular / Swagger UI
* AI assistance: ChatGPT was used for planning, clarification of assessment scope, architectural trade-off discussion, README drafting, and test-case brainstorming.
* Internet resources: listed in [`docs/resources.md`](docs/resources.md)

## Limitations and next steps

Not implemented in this prototype:

* real BLE communication
* mobile or desktop sync client
* frontend dashboard
* authentication
* role-based access control
* real participant identity management
* consent workflows
* production audit logs
* background workers
* cloud deployment
* large-scale time-series storage
* real-time streaming
* visualization

Next production steps would include PostgreSQL, authentication, study-scoped authorization, audit logging, data retention/privacy workflows, async export jobs, dashboard aggregation, and clearer sync contracts with firmware and mobile teams.
