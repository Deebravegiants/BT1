# [M] Denial of service in Mattermost

## Summary
Severity: Medium
Advisory: GHSA-5jph-wrq7-v9hf
CVE: CVE-2022-4044
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-23
Source: https://github.com/advisories/GHSA-5jph-wrq7-v9hf
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <7.1.4
- Go: `github.com/mattermost/mattermost-server` — affected >=7.2.0 <7.2.1
- Go: `github.com/mattermost/mattermost-server` — affected >=7.3.0 <7.3.1

## Details
A denial-of-service vulnerability in Mattermost allows an authenticated user to crash the server via multiple large autoresponder messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4044
- https://hackerone.com/reports/1680241
- https://mattermost.com/security-updates
