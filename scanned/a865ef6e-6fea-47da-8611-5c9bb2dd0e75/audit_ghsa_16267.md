# [M] Mattermost leaks details of AD/LDAP groups of a teams

## Summary
Severity: Medium
Advisory: GHSA-7v3v-984v-h74r
CVE: CVE-2024-23493
CWE: CWE-200, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-7v3v-984v-h74r
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.4.0 <9.4.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.3.0 <9.3.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.2.0 <9.2.5

## Details
Mattermost fails to properly authorize the requests fetching team associated AD/LDAP groups, allowing a user to fetch details of AD/LDAP groups of a team that they are not a member of.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23493
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
