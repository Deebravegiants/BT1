# [M] Mattermost denial of service through long emoji value

## Summary
Severity: Medium
Advisory: GHSA-6mx3-9qfh-77gj
CVE: CVE-2024-24988
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-6mx3-9qfh-77gj
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.3.0 <9.3.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.2.0 <9.2.5

## Details
Mattermost fails to properly validate the length of the emoji value in the custom user status, allowing an attacker to send multiple times a very long string as an emoji value causing high resource consumption and possibly crashing the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24988
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
