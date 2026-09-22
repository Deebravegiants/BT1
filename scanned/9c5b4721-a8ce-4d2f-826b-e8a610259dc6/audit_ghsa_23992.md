# [H] Mattermost Server vulnerable to Denial of Service through `@` character prefix inserted into JavaScript field names

## Summary
Severity: High
Advisory: GHSA-jc6w-8r7f-vmp5
CVE: CVE-2017-18871
CWE: CWE-248
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jc6w-8r7f-vmp5
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.2.2
- Go: `github.com/mattermost/mattermost-server` — affected >=4.3.0-rc1 <4.3.4
- Go: `github.com/mattermost/mattermost-server` — affected >=4.4.0-rc1 <4.4.5
- Go: `github.com/mattermost/mattermost-server` — affected >=4.5.0-rc1 <4.5.0

## Details
An issue was discovered in Mattermost Server before 4.5.0, 4.4.5, 4.3.4, and 4.2.2. It allows attackers to cause a denial of service (application crash) via an @ character before a JavaScript field name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18871
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
