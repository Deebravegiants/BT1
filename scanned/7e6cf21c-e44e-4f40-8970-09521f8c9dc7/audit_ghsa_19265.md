# [M] Mattermost Fails to Lockout LDAP Users After Repeated Login Failures

## Summary
Severity: Medium
Advisory: GHSA-qgwx-rffp-6cx9
CVE: CVE-2025-31947
CWE: CWE-645
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2025-05-15
Source: https://github.com/advisories/GHSA-qgwx-rffp-6cx9
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.6.0 <10.6.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.5.0 <10.5.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.4.0 <10.4.5
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.12
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250415054241-76ab3867b785

## Details
Mattermost versions 10.6.x <= 10.6.1, 10.5.x <= 10.5.2, 10.4.x <= 10.4.4, 9.11.x <= 9.11.11 fail to lockout LDAP users following repeated login failures, which allows attackers to lock external LDAP accounts through repeated login failures through Mattermost.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-31947
- https://github.com/mattermost/mattermost/pull/30821
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
