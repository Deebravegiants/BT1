# [H] Budibase authenticated arbitrary S3 signed upload URL issuance via `/api/attachments/:datasourceId/url`

## Summary
Severity: High
Advisory: GHSA-6x9p-4r67-5gjx
CVE: CVE-2026-54356
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-6x9p-4r67-5gjx
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0

## Details
### Summary
Budibase 3.39.7 allows a low-privilege authenticated published-app user with the built-in BASIC role to obtain arbitrary S3 pre-signed upload URLs backed by a workspace datasource's stored server-side credentials.

The affected endpoint is:

`POST /api/attachments/:datasourceId/url`

The caller can control:
```text
bucket
key
```
and receives:
```text
signedUrl
publicUrl
```

This lets a low-privilege published-app user mint S3 `PUT` URLs using server-side datasource credentials for attacker-chosen object destinations.

Steps:

1. Log in as an admin user.
2. Create a new app/workspace.
3. In the development app context, create an S3 datasource with valid credentials.
4. Publish the app.
5. Create a low-privilege user with the built-in BASIC role on the published production app ID.
6. Log in as that BASIC user.
7. Send:
`POST /api/attachments/<datasourceId>/url`

with:
```json
{"bucket":"foo","key":"bar"}
```
and the published app header:
```text
x-budibase-app-id: <published_app_id>
```
Observe a successful response containing:
```text
signedUrl
publicUrl
```

### Observed result

The following behavior:

dev BASIC request: 403 User does not have permission
app publish: SUCCESS
prod BASIC request: 200 OK
Example confirmed runtime values from the final successful run:
```text
prodAppId: app_e6b4cdc6cd6949969a83ff11eee88c5a
datasourceId: datasource_0cec491b26a742468257c62382aa3284
publicUrl: https://foo.s3.eu-west-1.amazonaws.com/bar
```
The returned signedUrl contained standard AWS signing markers, including:
```text
X-Amz-Credential=bb
X-Amz-Signature
X-Amz-Expires=900
```
### Impact

A low-privilege published-app user who knows a valid datasource ID can mint S3 upload URLs backed by server-side datasource credentials and choose arbitrary destination bucket and key values.

### Route definition
`packages/server/src/api/routes/static.ts:45`
Authorization logic
`packages/server/src/middleware/authorized.ts`
`packages/server/src/middleware/resourceId.ts`
Controller logic
`packages/server/src/api/controllers/static/index.ts`
Datasource lookup
`packages/server/src/sdk/workspace/datasources/datasources.ts`

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-6x9p-4r67-5gjx
- https://nvd.nist.gov/vuln/detail/CVE-2026-54356
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.41.3
