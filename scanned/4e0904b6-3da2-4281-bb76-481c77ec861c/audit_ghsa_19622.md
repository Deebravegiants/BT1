# [M] Mattermost Fails to Enforce Certain Search APIs

## Summary
Severity: Medium
Advisory: GHSA-3gpx-p63p-pr5r
CVE: CVE-2025-30179
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-03-21
Source: https://github.com/advisories/GHSA-3gpx-p63p-pr5r
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.4.0 <10.4.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.3.0 <10.3.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.9
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.5.0 <10.5.1

## Details
Mattermost versions 10.4.x <= 10.4.2, 10.3.x <= 10.3.3, 9.11.x <= 9.11.8 fail to enforce MFA on certain search APIs, which allows authenticated attackers to bypass MFA protections via user search, channel search, or team search queries.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-30179
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
