# [M] Channel member roles accept out-of-scope roles

## Summary
Severity: Medium
Advisory: CVE-2026-16048
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-16048
Type: osv

## Details
Mattermost versions 11.8.x <= 11.8.2, 11.7.x <= 11.7.6, 10.11.x <= 10.11.21 fail to restrict channel member role assignment to channel-scoped roles which allows a channel administrator to gain additional channel permissions via the channel member roles API.. Mattermost Advisory ID: MMSA-2026-00697

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16048.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-16048
