# [H] Mattermost post fetching without auditing in compliance export 

## Summary
Severity: High
Advisory: GHSA-fx48-xv6q-6gp3
CVE: CVE-2024-1887
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-fx48-xv6q-6gp3
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.3.0 <9.3.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.2.0 <9.2.5
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.1.9

## Details
Mattermost fails to check if compliance export is enabled when fetching posts of public channels allowing a user that is not a member of the public channel to fetch the posts, which will not be audited in the compliance export.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1887
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
