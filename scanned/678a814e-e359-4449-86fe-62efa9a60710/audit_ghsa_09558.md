# [M] NocoDB: Missing File Size Enforcement in Upload-by-URL Allows Denial of Service via Disk Exhaustion

## Summary
Severity: Medium
Advisory: GHSA-99vc-2jx2-688p
CVE: CVE-2026-46551
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-99vc-2jx2-688p
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0

## Details
### Summary

The `uploadViaURL` path in the v1/v2 attachment API did not enforce `NC_ATTACHMENT_FIELD_SIZE` against the remote `content-length` or against the response stream. An authenticated user (Editor+) could direct the server to download arbitrarily large files, exhausting disk space and causing denial of service.

### Details

In `packages/nocodb/src/services/attachments.service.ts`, the HEAD probe read `content-length` but never compared it to `NC_ATTACHMENT_FIELD_SIZE`; the subsequent `storageAdapter.fileCreateByUrl()` performed the download without `maxContentLength`. The v3 service (`v3/data-attachment-v3.service.ts`) already enforced the limit, but the v1/v2 endpoints (`POST /api/v1/db/storage/upload-by-url`, `POST /api/v2/storage/upload-by-url`) did not.

This is distinct from GHSA-xr7v-j379-34v9 (blind SSRF via HEAD) — same code area, different class.

### Impact

- Authenticated DoS via disk exhaustion. Editor role suffices.
- Cascading failures once disk fills: blocked DB writes, log rotation, application crash.

### Credit

This issue was reported by [@ik0z](https://github.com/ik0z).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-99vc-2jx2-688p
- https://nvd.nist.gov/vuln/detail/CVE-2026-46551
- https://github.com/nocodb/nocodb
