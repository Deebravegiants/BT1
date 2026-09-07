# [M] Cross-site Scripting in Mattermost

## Summary
Severity: Medium
Advisory: GHSA-hv5f-73mr-7vvj
CVE: CVE-2021-37860
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-23
Source: https://github.com/advisories/GHSA-hv5f-73mr-7vvj
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v5` — affected >=0 <5.39.0

## Details
Mattermost 5.38 and earlier fails to sufficiently sanitize clipboard contents, which allows a user-assisted attacker to inject arbitrary web script in product deployments that explicitly disable the default CSP.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37860
- https://docs.mattermost.com/install/self-managed-changelog.html#release-v5-39-quality-release
- https://github.com/mattermost/mattermost-server
- https://mattermost.com/security-updates
