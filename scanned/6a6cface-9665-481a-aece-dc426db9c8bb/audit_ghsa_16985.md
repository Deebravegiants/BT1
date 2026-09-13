# [M] Mattermost Server Improper Access Control 

## Summary
Severity: Medium
Advisory: GHSA-w67v-ph4x-f48q
CVE: CVE-2024-29221
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-04-05
Source: https://github.com/advisories/GHSA-w67v-ph4x-f48q
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.1.0 <8.1.11
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.4.0 <9.4.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.3.0 <9.3.3

## Details
Improper Access Control in Mattermost Server versions 9.5.x before 9.5.2, 9.4.x before 9.4.4, 9.3.x before 9.3.3, 8.1.x before 8.1.11 lacked proper access control in the `/api/v4/users/me/teams` endpoint allowing a team admin to get the invite ID of their team, thus allowing them to invite users, even if the "Add Members" permission was explicitly removed from team admins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29221
- https://github.com/mattermost/mattermost/commit/0dc03fbc6e3c9afb14137e72ab3fa6f5a0125b9c
- https://github.com/mattermost/mattermost/commit/5cce9fed7363386afebd81a58fb5fab7d2729c8f
- https://github.com/mattermost/mattermost/commit/a5784f34ba6592c6454b8742f24af9d06279e347
- https://github.com/mattermost/mattermost/commit/dd3fe2991a70a41790d6bef5d31afc5957525f3c
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2024-2706
