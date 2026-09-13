# [M] Boards plugin panics on WebSocket command with non-string field types

## Summary
Severity: Medium
Advisory: CVE-2026-10080
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-10080
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.6, 10.11.x <= 10.11.21, 11.8.x <= 11.8.3 fails to validate WebSocket command field types which allows an authenticated user to crash the plugin process and deny service to all Boards users via a custom_focalboard_SUBSCRIBE_TEAM message with a non-string teamId.. Mattermost Advisory ID: MMSA-2026-00687

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10080.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-10080
