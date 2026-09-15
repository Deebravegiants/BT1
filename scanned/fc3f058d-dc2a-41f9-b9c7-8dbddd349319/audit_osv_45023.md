# [H] Insufficient server-side validation of board member role fields permits privilege escalation

## Summary
Severity: High
Advisory: CVE-2026-9816
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-9816
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.6, 10.11.x <= 10.11.21, 11.8.x <= 11.8.3 fail to validate BoardMember.Scheme* fields server-side on insert and archive-import paths which allows a board editor or non-guest team member to grant board admin to arbitrary users via POST /api/v2/boards/{boardID}/members and POST /api/v2/teams/{teamID}/archive/import.. Mattermost Advisory ID: MMSA-2026-00685

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9816.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-9816
