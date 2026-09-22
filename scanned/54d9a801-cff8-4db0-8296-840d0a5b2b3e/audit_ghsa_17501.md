# [M] Mattermost allows authenticated administrator to execute LDAP search filter injection

## Summary
Severity: Medium
Advisory: GHSA-4r67-4x4p-fprg
CVE: CVE-2025-4573
CWE: CWE-90
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-06-11
Source: https://github.com/advisories/GHSA-4r67-4x4p-fprg
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250414112942-77892234944b
- Go: `github.com/mattermost/mattermost-server` — affected >=10.7.0 <10.7.2
- Go: `github.com/mattermost/mattermost-server` — affected >=10.6.0 <10.6.4
- Go: `github.com/mattermost/mattermost-server` — affected >=10.5.0 <10.5.5
- Go: `github.com/mattermost/mattermost-server` — affected >=9.11.0 <9.11.14

## Details
Mattermost versions 10.7.x <= 10.7.1, 10.6.x <= 10.6.3, 10.5.x <= 10.5.4, 9.11.x <= 9.11.13 fail to properly validate LDAP group ID attributes, allowing an authenticated administrator with PermissionSysconsoleWriteUserManagementGroups permission to execute LDAP search filter injection via the PUT /api/v4/ldap/groups/{remote_id}/link API when objectGUID is configured as the Group ID Attribute.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4573
- https://github.com/mattermost/mattermost/commit/1f9c688a30847eeb7bfb1574dc7bbb9f011afbf7
- https://github.com/mattermost/mattermost/commit/64a65c6107877382040297b3ef215c689caaed74
- https://github.com/mattermost/mattermost/commit/77892234944bc7476b20794e516538bcac717de9
- https://github.com/mattermost/mattermost/commit/b33926709b956a59558cc7fef80c0e75a769ce81
- https://github.com/mattermost/mattermost/commit/b47e89c4f98cb6ad9f1dceb79325aa94e80f963a
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
