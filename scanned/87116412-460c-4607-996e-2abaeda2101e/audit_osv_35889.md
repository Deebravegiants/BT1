# [M] Board channel linking without read channel permission validation

## Summary
Severity: Medium
Advisory: CVE-2026-16047
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-16047
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.6, 10.11.x <= 10.11.21, 11.8.x <= 11.8.3 fail to validate that users have read access to a channel before linking a board to it, which allows an authenticated attacker to discover the membership of private channels on the same team via creating, patching, importing, or bulk-creating boards with an arbitrary channelId. Mattermost Advisory ID: MMSA-2026-00674

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16047.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-16047
