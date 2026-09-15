# [M] Improper Input Validation in Zoom Plugin Webhook Handler

## Summary
Severity: Medium
Advisory: CVE-2026-3116
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-3116
Type: osv

## Details
Mattermost Plugins versions <=11.4 11.0.4 11.1.3 11.3.2 10.11.11.0 fail to validate incoming request size which allows an authenticated attacker to cause service disruption via the webhook endpoint. Mattermost Advisory ID: MMSA-2026-00589

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3116.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-3116
