# [M] Mattermost Plugin Channel Export excessive resource consumption

## Summary
Severity: Medium
Advisory: GHSA-869f-px86-vj84
CVE: CVE-2024-43105
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-08-23
Source: https://github.com/advisories/GHSA-869f-px86-vj84
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-channel-export` — affected >=0 <1.0.1

## Details
Mattermost Plugin Channel Export versions <=1.0.0 fail to restrict concurrent runs of the /export command which allows a user to consume excessive resource by running the /export command multiple times at once.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43105
- https://github.com/mattermost/mattermost-plugin-channel-export/commit/bb6da1f6bedd6cefe2276d6493b5541843c543a6
- https://github.com/mattermost/mattermost-plugin-channel-export
- https://mattermost.com/security-updates
