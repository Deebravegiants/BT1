# [M] OpenReception: GET appointment by ID returns full appointment record without authorization

## Summary
Severity: Medium
Advisory: CVE-2026-48077
Aliases: GHSA-8547-9x2c-9vmf
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-48077
Type: osv

## Details
OpenReception's appointment booking software provides an end-to-end encrypted appointment booking platform. Prior to version 1.1.0, the GET handler at `/api/tenants/{id}/appointments/{appointmentId}` performs no authorization check before returning the appointment record. Any party who knows or obtains a valid appointment UUID receives the full row, including channel and agent IDs, time and timezone, status, and the AES-GCM ciphertext components (`encryptedPayload`, `iv`, `authTag`, `dataKey`). The same file's DELETE handler calls `checkPermission(locals, tenantId, true)` before allowing deletion. The intent is clear: appointment records are tenant-scoped and require authentication to access. The GET handler is missing the equivalent call. The middleware chain (`apiAuthHandle`, `authGuard`) does not compensate: API paths bypass `authGuard` entirely, and `apiAuthHandle` does not block requests to non-admin paths when no token is present. Version 1.1.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48077.json
- https://github.com/open-reception/appointment-booking-software/security/advisories/GHSA-8547-9x2c-9vmf
- https://nvd.nist.gov/vuln/detail/CVE-2026-48077
- https://github.com/open-reception/appointment-booking-software/commit/16474d96c591e246a103b9d6aa15ca30d436d11b
