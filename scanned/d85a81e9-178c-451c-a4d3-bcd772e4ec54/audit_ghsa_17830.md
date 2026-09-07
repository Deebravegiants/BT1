# [M] Mattermost Incorrect Type Conversion or Cast

## Summary
Severity: Medium
Advisory: GHSA-8j3q-gc9x-7972
CVE: CVE-2025-21088
CWE: CWE-704
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-01-15
Source: https://github.com/advisories/GHSA-8j3q-gc9x-7972
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.2.0 <10.2.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.1.0 <10.1.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.0.0 <10.0.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20241127161322-25ff7a3779a5

## Details
Mattermost versions 10.2.x <= 10.2.0, 9.11.x <= 9.11.5, 10.0.x <= 10.0.3, 10.1.x <= 10.1.3 fail to properly validate the style of proto supplied to an action's style in post.props.attachments, which allows an attacker to crash the frontend via crafted malicious input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-21088
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2025-3393
