# [H]  Budibase: S3 presigned URL endpoint authorization regression in v3.39.4 allows BASIC users to obtain S3 PutObject presigned URLs

## Summary
Severity: High
Advisory: GHSA-xcx6-4f2g-hhgx
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-xcx6-4f2g-hhgx
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0

## Details
## Impact

In Budibase v3.39.4, a regression in the authorization level for the S3 attachment upload endpoint allows any BASIC app user to obtain S3 PutObject presigned URLs. The endpoint uses TABLE/WRITE permission level instead of the intended BUILDER level defined in v3.39.3. Additionally, the controller does not pin the target bucket to the datasource's configured bucket, allowing writes to any S3 bucket the stored IAM credentials can access.

## Reproduction

1. As a BASIC app user, discover or obtain a valid S3 datasource ID within the app
2. Send a POST request:

```
POST /api/attachments/<datasourceId>/url
Content-Type: application/json
x-budibase-app-id: <appId>

{"bucket": "target-bucket", "key": "malicious-file.html"}
```

3. The response contains a valid S3 PutObject presigned URL
4. Use the presigned URL to upload arbitrary content to any writable S3 bucket in the IAM credential scope

## Root Cause

The `/api/attachments/:datasourceId/url` route was changed from `authorized(BUILDER)` in v3.39.3 to `authorized(PermissionType.TABLE, PermissionLevel.WRITE)` in v3.39.4. BASIC users have TABLE/WRITE permissions by default, so they can call this endpoint. The controller at `packages/server/src/api/controllers/static/index.ts:614-632` accepts the `bucket` parameter directly from the request body and passes it to `getSignedUrl` without validating against the datasource's configured bucket.

## Evidence

The test suite at `packages/server/src/api/routes/tests/static.spec.ts:218-235` confirms this behavior. The test authenticates as a BASIC role user and successfully generates a signed upload URL, verifying HTTP 200 and a defined `res.body.signedUrl`.

## Remediation

1. Restore the `authorized(BUILDER)` middleware on the route
2. Add `paramResource("datasourceId")` to ensure the datasource belongs to the caller's app
3. Pin the S3 bucket to `datasource.config.bucket` in the controller, ignoring the caller-supplied bucket value

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-xcx6-4f2g-hhgx
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.40.0
