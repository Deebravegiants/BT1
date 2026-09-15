# [M] Mattermost is vulnerable to DoS due to infinite re-renders on API errors

## Summary
Severity: Medium
Advisory: GHSA-mx8m-v8qm-xwr8
CVE: CVE-2025-14435
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-mx8m-v8qm-xwr8
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.9
- Go: `github.com/mattermost/mattermost-server` — affected >=11.1.0 <11.1.2
- Go: `github.com/mattermost/mattermost-server` — affected >=11.0.0 <11.0.7

## Details
Mattermost versions 10.11.x <= 10.11.8, 11.1.x <= 11.1.1, 11.0.x <= 11.0.6 fail to prevent infinite re-renders on API errors which allows authenticated users to cause application-level DoS via triggering unbounded component re-render loops.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14435
- https://github.com/mattermost/mattermost/commit/613bb616cd62c584a606919e6978688e7b87d81e
- https://github.com/mattermost/mattermost/commit/9f7629504bc93f79af8d606329c025a687e143cd
- https://github.com/mattermost/mattermost/commit/cc6b77b271324796b72f1e6b82dba85a86462f9f
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2026-4326
