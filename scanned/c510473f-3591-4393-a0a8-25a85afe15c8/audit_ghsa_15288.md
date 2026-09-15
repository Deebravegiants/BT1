# [M] Mattermost doesn't restrict which roles can promote a user as system admin

## Summary
Severity: Medium
Advisory: GHSA-5263-pm2h-m7hw
CVE: CVE-2024-8071
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-08-22
Source: https://github.com/advisories/GHSA-5263-pm2h-m7hw
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.9.0 <9.9.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.8
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.10.0 <9.10.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.8.0 <9.8.3

## Details
Mattermost versions 9.9.x <= 9.9.1, 9.5.x <= 9.5.7, 9.10.x <= 9.10.0 and 9.8.x <= 9.8.2 fail to restrict which roles can promote a user as system admin which allows a System Role with edit access to the permissions section of system console to update their role (e.g. member) to include the `manage_system` permission, effectively becoming a System Admin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8071
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
