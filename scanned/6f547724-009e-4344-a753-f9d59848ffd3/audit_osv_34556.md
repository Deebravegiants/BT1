# [C] FlagForge Allows Unauthenticated Badge Template API Access

## Summary
Severity: Critical
Advisory: CVE-2025-61777
Aliases: GHSA-26rx-c53q-rjf9
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-10-06
Source: https://osv.dev/vulnerability/CVE-2025-61777
Type: osv

## Details
Flag Forge is a Capture The Flag (CTF) platform. Starting in version 2.0.0 and prior to version 2.3.2, the `/api/admin/badge-templates` (GET) and `/api/admin/badge-templates/create` (POST) endpoints previously allowed access without authentication or authorization. This could have enabled unauthorized users to retrieve all badge templates and sensitive metadata (createdBy, createdAt, updatedAt) and/or create arbitrary badge templates in the database. This could lead to data exposure, database pollution, or abuse of the badge system. The issue has been fixed in FlagForge v2.3.2. GET, POST, UPDATE, and DELETE endpoints now require authentication. Authorization checks ensure only admins can access and modify badge templates. No reliable workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61777.json
- https://github.com/FlagForgeCTF/flagForge/security/advisories/GHSA-26rx-c53q-rjf9
- https://nvd.nist.gov/vuln/detail/CVE-2025-61777
- https://github.com/FlagForgeCTF/flagForge/commit/e2121c5fb7a512a49dcd875812c944265fb1a846
