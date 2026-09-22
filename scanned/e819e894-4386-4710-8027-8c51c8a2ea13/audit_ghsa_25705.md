# [M] Resource exhaustion in Mattermost

## Summary
Severity: Medium
Advisory: GHSA-f37q-q7p2-ccfc
CVE: CVE-2022-1337
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-14
Source: https://github.com/advisories/GHSA-f37q-q7p2-ccfc
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <6.4.2

## Details
The image proxy component in Mattermost version 6.4.1 and earlier allocates memory for multiple copies of a proxied image, which allows an authenticated attacker to crash the server via links to very large image files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1337
- https://github.com/mattermost/mattermost-server
- https://mattermost.com/security-updates
