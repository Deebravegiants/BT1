# [M] Transmute has full-read SSRF in URL file import (POST /api/files/url) — no host/IP validation, follows redirects

## Summary
Severity: Medium
Advisory: CVE-2026-54054
Aliases: GHSA-89m5-mvmx-7xrf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-54054
Type: osv

## Details
Transmute is a free, open-source, self-hosted file conversion and compression tool. Prior to version 1.3.0, Transmute's URL import endpoint, `POST /api/files/url`, is vulnerable to Server-Side Request Forgery (SSRF). The HTTP downloader used by this endpoint fetches user-supplied URLs with redirects enabled and does not validate whether the target resolves to a public, external address. As a result, an authenticated user (or guest user if they are enabled) may be able to cause the Transmute server to make HTTP requests to internal or cloud-local resources from the server's network position. Because downloaded content is stored and can later be retrieved through `GET /api/files/{id}`, this issue can result in full-read SSRF rather than blind SSRF. This is fixed in version 1.3.0.

## References
- https://github.com/transmute-app/transmute/releases/tag/v1.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54054.json
- https://github.com/transmute-app/transmute/security/advisories/GHSA-89m5-mvmx-7xrf
- https://nvd.nist.gov/vuln/detail/CVE-2026-54054
