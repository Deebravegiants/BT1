# [M] Twenty: SSRF protection bypass via HTTP redirect following in secure HTTP client

## Summary
Severity: Medium
Advisory: CVE-2026-27023
Aliases: GHSA-wm7q-rvq3-x8q9
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-27023
Type: osv

## Details
Twenty is an open source CRM. Prior to version 1.18, the SSRF protection in SecureHttpClientService validated request URLs at the request level but did not validate redirect targets. An authenticated user who could control outbound request URLs (e.g., webhook endpoints, image URLs) could bypass private IP blocking by redirecting through an attacker-controlled server. This issue has been patched in version 1.18.

## References
- https://github.com/twentyhq/twenty/releases/tag/v1.18.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27023.json
- https://github.com/twentyhq/twenty/security/advisories/GHSA-wm7q-rvq3-x8q9
- https://nvd.nist.gov/vuln/detail/CVE-2026-27023
