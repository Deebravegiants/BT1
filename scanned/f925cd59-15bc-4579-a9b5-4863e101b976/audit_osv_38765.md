# [M] Coolify: SSRF via S3 Storage Endpoint in testConnection()

## Summary
Severity: Medium
Advisory: CVE-2026-42147
Aliases: GHSA-pwm4-w33c-wjf3
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-42147
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.474, S3 storage endpoint validation only checks URL format and testConnection() sends a server-side request to the configured endpoint, allowing an authenticated user with storage management permissions to make Coolify request internal or metadata-service URLs. This issue is fixed in version 4.0.0-beta.474.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.474
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42147.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-pwm4-w33c-wjf3
- https://nvd.nist.gov/vuln/detail/CVE-2026-42147
- https://github.com/coollabsio/coolify/commit/297e9c41e19958f6237919794c28c3fb1d4cda32
