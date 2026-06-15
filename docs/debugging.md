# Debugging Investigation

## Issue A — Sensor Data Missing or Duplicated After Sync

Researchers report that some study sessions show missing IMU or PPG samples, while other sessions contain duplicated records after mobile/desktop sync. The embedded and mobile teams say the ring appears to be collecting data correctly.

### Likely root causes

Possible causes across the system:

* sync client retries the same upload without a stable `batch_id`
* backend does not enforce idempotency
* duplicate batches accepted after network timeouts
* same readings included in multiple batches
* partial BLE reads from the ring
* ring deletes data before backend confirmation
* ring storage fills before sync completes
* missing or reset sequence numbers
* timestamp drift or incorrect timestamp conversion
* mobile client loses local sync state
* concurrent sync attempts from multiple clients
* frontend or export layer displays duplicated records due to bad joins or repeated fetches
* dashboard filters hide some readings
* rejected batches are not visible to researchers or support team

### Debugging process

I would trace one affected session end to end:

1. Identify affected study/session/device/sensor type.
2. Compare expected sample ranges with stored backend readings.
3. Check batch IDs received by the API.
4. Check whether duplicate `batch_id`s were accepted.
5. Check sequence numbers and timestamps for gaps or overlaps.
6. Review API logs for rejected or partially failed batches.
7. Review sync client logs for retry behavior, offline periods, and BLE transfer failures.
8. Confirm whether the same ring was synced by more than one client.
9. Check whether the frontend/export query is duplicating rows.
10. Compare backend stored data with exported/dashboard data.

Useful tools:

* backend request logs
* database queries
* sync client logs
* device/session/batch audit logs
* sequence/timestamp gap checks
* frontend network inspector
* export file inspection
* error monitoring and metrics

### Immediate mitigations

* enforce uniqueness on `device + batch_id`
* return explicit duplicate responses
* log rejected batches and reasons
* add API logs for batch size, session, device, sensor type, and received sequence range
* expose sync status per session/device
* add basic gap detection using `sequence_number` if available
* verify frontend/export queries do not duplicate readings

### Design changes to consider

* stable batch IDs preserved across retries
* reading-level sequence numbers from firmware
* backend uniqueness constraints
* atomic batch ingestion
* sync status/audit table
* rejected batch log
* confirmation-before-delete strategy for device/mobile storage
* recovery sync endpoint for missing ranges
* dashboard warnings for detected gaps

---

## Issue B — Dashboard and Export Performance Degrade With Larger Studies

A researcher runs a 7-day study with 50 participants. The dashboard becomes slow, CSV/JSON exports take several minutes, and some export requests fail.

### Likely bottlenecks

* too many raw readings loaded into dashboard views
* high-frequency IMU data creates large database tables quickly
* unindexed queries by session, device, sensor type, or timestamp
* synchronous export generation blocks request/response cycle
* large JSON/CSV responses time out
* memory usage spikes while building export files
* frontend renders too many points at once
* no pagination
* no downsampling or aggregation
* database JSON fields are hard to query efficiently at scale
* repeated dashboard queries recalculate the same data
* export endpoint lacks streaming or background processing

### Debugging process

1. Identify slow endpoints.
2. Check database query counts and query plans.
3. Measure response times for dashboard and export endpoints.
4. Compare raw reading counts per session/sensor.
5. Check whether dashboard loads raw or aggregated data.
6. Inspect server memory and CPU during export.
7. Check timeout logs and failed requests.
8. Test exports with smaller time ranges to find thresholds.
9. Review indexes on session, device, sensor type, and timestamp.
10. Check frontend rendering and network payload size.

Useful tools:

* Django Debug Toolbar locally
* database query logs
* `EXPLAIN` query plans
* application logs
* server metrics
* browser DevTools
* error monitoring
* profiling around export generation

### Immediate fixes

* add indexes for common query patterns
* paginate raw readings
* restrict dashboard default date ranges
* avoid loading all raw readings into dashboard charts
* stream CSV responses if feasible
* add request limits and clearer error responses
* reduce export memory usage
* add progress/error logging around exports

### Longer-term changes

* move to PostgreSQL
* use async/background export jobs
* store generated export files in object storage
* add downsampled dashboard views
* precompute aggregates
* partition readings by study/session/date
* separate raw storage from dashboard query models
* consider time-series storage depending on access patterns
* add monitoring for ingestion latency, query time, export duration, and failure rates

---

## Issue C — Signup or Onboarding Flow Breaks After an Update

After a recent website or application update, some users can no longer complete developer signup or researcher onboarding. Analytics also show lower conversion and slower page loads.

### Likely root causes

* frontend regression in signup/onboarding form
* API contract changed without frontend update
* validation rules became stricter
* authentication/session/cookie issue
* third-party service failure
* email verification problem
* analytics event names changed or stopped firing
* JavaScript error on specific browsers/devices
* performance regression from larger bundles or slow API calls
* database migration or backend deployment issue
* feature flag misconfiguration
* WordPress/plugin/theme update conflict if onboarding touches the marketing site

### Debugging process

1. Reproduce the affected signup/onboarding flows.
2. Segment by user type, browser, device, geography, and entry path.
3. Check frontend error logs.
4. Check backend API errors.
5. Inspect analytics funnel drop-off points.
6. Compare recent release changes.
7. Check page load metrics and Core Web Vitals.
8. Verify third-party dependencies such as email, auth, analytics, or payment tools.
9. Check whether the issue affects all users or only a subset.
10. Roll back or hotfix if the business impact is high.

Useful tools:

* browser DevTools
* frontend error monitoring
* backend logs
* analytics funnel reports
* performance monitoring
* release diff
* synthetic checks
* server metrics
* user session replay, if privacy-compliant

### Immediate stabilization

* roll back the release if the issue is severe
* hotfix the broken form/API contract
* disable the faulty feature flag
* add temporary monitoring around the affected flow
* communicate internally about affected users
* preserve logs and examples for root-cause analysis

### Design and process improvements

* end-to-end tests for signup and onboarding
* API contract tests
* staged rollouts
* feature flags with safe defaults
* release checklist for critical flows
* monitoring and alerts on conversion drops
* performance budgets
* synthetic signup/onboarding checks
* better analytics event versioning
* clearer ownership of WordPress/app/backend release dependencies
