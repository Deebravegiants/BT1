# [M] Parseable < 2.9.2 - Cleartext Credential Exposure in Notification Target API

## Summary
Severity: Medium
Advisory: CVE-2026-56783
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-56783
Type: osv

## Details
Parseable before 2.9.2 contains an information disclosure vulnerability in the notification-target API endpoints that returns webhook tokens and basic-auth credentials in cleartext due to commented-out secret-masking functionality. Any authenticated user with the GetAlert action, including low-privilege reader roles, can recover credentials and internal endpoint URLs for all configured notification targets by querying GET /api/v1/targets or related endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56783.json
- https://github.com/parseablehq/parseable/releases/tag/v2.9.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-56783
- https://www.vulncheck.com/advisories/parseable-cleartext-credential-exposure-in-notification-target-api
- https://github.com/parseablehq/parseable/issues/1693
- https://github.com/parseablehq/parseable/pull/1698
- https://github.com/parseablehq/parseable/commit/f307c4989cc9f3ff4204fd383dec7a39924e6b2a
- https://github.com/parseablehq/parseable
