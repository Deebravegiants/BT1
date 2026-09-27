# [M] Mattermost Boards plugin didn’t enforce role-based authorization on board channel link allowing board editors to expose boards to arbitrary channels

## Summary
Severity: Medium
Advisory: CVE-2026-9859
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-9859
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.6, 10.11.x <= 10.11.21, 11.8.x <= 11.8.3 fail to enforce PermissionManageBoardRoles on the channelId field of the batch endpoint, which allows an authenticated board editor to relink any board they can edit to an arbitrary channel via a crafted PATCH request. Mattermost Advisory ID: MMSA-2026-00686

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9859.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-9859
