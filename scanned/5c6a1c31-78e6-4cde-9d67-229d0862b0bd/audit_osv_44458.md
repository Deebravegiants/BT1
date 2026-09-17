# [M] Documenso before 2.13.0 Unauthenticated File Upload via /api/files/upload-pdf

## Summary
Severity: Medium
Advisory: CVE-2026-82472
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82472
Type: osv

## Details
Documenso before 2.13.0 accepts PDF file uploads on the /api/files/upload-pdf endpoint without requiring authentication, session tokens, or API credentials. Unauthenticated attackers can upload arbitrary PDF files indefinitely to exhaust storage resources or fill the database with unlinked document records.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82472.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82472
- https://www.vulncheck.com/advisories/documenso-before-2.13.0-unauthenticated-file-upload-via-api-files-upload-pdf
- https://github.com/documenso/documenso/commit/4f346d3c2d5264f221e4d787e162f16051e44114
- https://github.com/documenso/documenso
- https://github.com/documenso/documenso/blob/v2.12.0/apps/remix/server/api/files/files.ts
