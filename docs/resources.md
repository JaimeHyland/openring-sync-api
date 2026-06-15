# Resources and Tools

## Tools used

* IDE: Visual Studio Code
* Backend framework: Django
* API framework: Django REST Framework
* Database: SQLite for local assessment implementation
* API documentation: drf-spectacular / Swagger UI
* Testing: pytest / pytest-django or Django test runner
* AI assistance: ChatGPT

## AI usage

AI assistance was used for:

* clarifying the assessment scope
* planning the MVP architecture
* discussing sync-client/backend boundaries
* identifying validation and idempotency concerns
* drafting README and documentation structure
* brainstorming tests and debugging scenarios

Final implementation decisions, code review, and submitted content were reviewed and adapted by me.

## Internet resources consulted

Add actual links/resources here as used.

Suggested categories:

* Django documentation
* Django REST Framework documentation
* drf-spectacular documentation
* pytest / pytest-django documentation
* OWASP API Security Top 10
* GDPR or ICO guidance on anonymization/pseudonymization
* BLE or wearable sync references, if consulted
* relevant hardware/sensor datasheets, if consulted

Example format:

```md
- Django documentation — used for model/API setup and local development reference.
- Django REST Framework documentation — used for serializers, views, and API testing.
- drf-spectacular documentation — used for OpenAPI/Swagger setup.
- pytest-django documentation — used for test configuration.
- OWASP API Security Top 10 — used as a reference for production API security considerations.
```

## Notes on sources

The implementation does not depend on exact sensor datasheet behavior. For the MVP, the backend assumes that the sync client has already decoded device-level data into normalized JSON batches.

Firmware-level details such as binary record framing, sampling rates, compression, sequence numbers, and clock drift should be confirmed with firmware and mobile teams before a production sync protocol is finalized.
