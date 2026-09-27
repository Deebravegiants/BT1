# [H] Mailu missing authentication on PATCH /api/v1/token/<id>, which allows unauthenticated removal of IP restrictions

## Summary
Severity: High
Advisory: CVE-2026-49217
Aliases: GHSA-2w8v-6xr5-g9gh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-49217
Type: osv

## Details
Mailu is a mail server as a set of Docker images. Prior to version 2024.06.52, a missing authorization check in the Mailu admin REST API allows any unauthenticated attacker to remove any potential IP restriction or update the comment field from any existing user token provided the REST API is enabled. Upgrade to Mailu 2024.06.52 to receive a patch or, as a workaround, turn the REST API off.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49217.json
- https://github.com/Mailu/Mailu/security/advisories/GHSA-2w8v-6xr5-g9gh
- https://nvd.nist.gov/vuln/detail/CVE-2026-49217
