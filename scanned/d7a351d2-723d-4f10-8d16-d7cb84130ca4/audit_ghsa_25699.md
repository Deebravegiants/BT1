# [H] Insecure plugin handling in Mattermost

## Summary
Severity: High
Advisory: GHSA-32rp-q37p-jg6w
CVE: CVE-2022-1384
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-20
Source: https://github.com/advisories/GHSA-32rp-q37p-jg6w
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=6.4.0 <6.5.0

## Details
Mattermost version 6.4.x and earlier fails to properly check the plugin version when a plugin is installed from the Marketplace, which allows an authenticated and an authorized user to install and exploit an old plugin version from the Marketplace which might have known vulnerabilities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1384
- https://mattermost.com/security-updates
- github.com/mattermost/mattermost-server
