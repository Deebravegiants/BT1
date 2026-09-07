# [M] Payload has Insufficient Filename Validation in Client-Upload Signed-URL Endpoints

## Summary
Severity: Medium
Advisory: GHSA-frq9-7j6g-v74x
CVE: CVE-2026-34750
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-frq9-7j6g-v74x
Type: github-advisory

## Affected
- npm: `@payloadcms/storage-azure` — affected >=0 <3.78.0
- npm: `@payloadcms/storage-gcs` — affected >=0 <3.78.0
- npm: `@payloadcms/storage-r2` — affected >=0 <3.78.0
- npm: `@payloadcms/storage-s3` — affected >=0 <3.78.0

## Details
### Impact

The client-upload signed-URL endpoints for S3, GCS, Azure, and R2 did not properly sanitize filenames. An attacker could craft filenames to escape the intended storage location.

Consumers are affected if ALL of these are true:

- Payload version **< v3.78.0**
- Using client-upload signed-URL endpoints for any supported storage adapter

  ## Patches

This vulnerability has been patched in **v3.78.0**. Filename validation has been hardened for client uploads.

Consumers should upgrade to **v3.78.0** or later.

## Workarounds

Consumers can upgrade:

- Limit access to client-upload signed-URL endpoints to trusted users only.

## References
- https://github.com/payloadcms/payload/security/advisories/GHSA-frq9-7j6g-v74x
- https://nvd.nist.gov/vuln/detail/CVE-2026-34750
- https://github.com/payloadcms/payload
