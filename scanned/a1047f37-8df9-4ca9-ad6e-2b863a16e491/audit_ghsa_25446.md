# [M] Mattermost Server exposes private team invite ID 

## Summary
Severity: Medium
Advisory: GHSA-c253-8hr4-r8v9
CVE: CVE-2017-18901
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c253-8hr4-r8v9
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <3.10.3
- Go: `github.com/mattermost/mattermost-server` — affected >=4.0.0 <4.0.4

## Details
An issue was discovered in Mattermost Server before 4.1.0, 4.0.4, and 3.10.3. It allows attackers to discover a team invite ID by requesting a JSON document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18901
- https://github.com/mattermost/mattermost/commit/5e822a7d09214d5446d54e02a0611df8e64f3aa5
- https://github.com/mattermost/mattermost/commit/638c38cc0d2296335a0fbd5bde8b6d2cbf9f9062
- https://github.com/mattermost/mattermost/commit/a78ed923f1c73ae5551893374fb9803ee2f4c8e6
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
