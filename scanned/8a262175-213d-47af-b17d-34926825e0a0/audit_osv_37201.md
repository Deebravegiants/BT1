# [M] CVE-2026-29197

## Summary
Severity: Medium
Advisory: CVE-2026-29197
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-29197
Type: osv

## Details
In versions <8.4.0, <8.3.2, <8.2.2, <8.1.3, <8.0.4, <7.13.6, <7.12.7, <7.11.7, and <7.10.10, the endpoints /api/apps/logs and /api/apps/:id/logs have a typo in the required permission check, allowing authenticated users without the proper permissions to read apps-engine logs.

## References
- https://hackerone.com/reports/3589551
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29197.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29197
- https://github.com/RocketChat/Rocket.Chat/pull/40125
