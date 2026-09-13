# [M] Mattermost denial of service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xvq6-h898-wcj8
CVE: CVE-2023-5967
CWE: CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-11-06
Source: https://github.com/advisories/GHSA-xvq6-h898-wcj8
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <7.8.12
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0 <8.0.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.1.0 <8.1.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.0.0 <9.0.1

## Details
Mattermost fails to properly validate requests to the Calls plugin, allowing an attacker sending a request without a User Agent header to cause a panic and crash the Calls plugin

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5967
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
