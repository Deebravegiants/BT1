# [M] Authenticated remote cluster can modify or delete posts it does not own in Mattermost Connected Workspaces shared channels

## Summary
Severity: Medium
Advisory: CVE-2026-10103
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-10103
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.2, 11.6.x <= 11.6.4, 10.11.x <= 10.11.19 fail to verify post ownership in the shared channel inbound sync handler, which allows an authenticated remote cluster to modify or delete posts authored by local users or other remotes via crafted sync messages referencing arbitrary post IDs in channels shared with that remote.. Mattermost Advisory ID: MMSA-2026-00689

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10103.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-10103
