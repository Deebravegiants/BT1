# [M] Mattermost has CSRF vulnerability via Calls Widget page

## Summary
Severity: Medium
Advisory: GHSA-gmx5-frv9-9m9f
CVE: CVE-2025-62190
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-12-17
Source: https://github.com/advisories/GHSA-gmx5-frv9-9m9f
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-calls` — affected >=0 <1.10.0

## Details
Mattermost versions 11.0.x < 11.0.4, 10.12.x <= 10.12.2, 10.11.x < 10.11.6 and Mattermost Calls versions < 1.10.0 fail to implement CSRF protection on the Calls widget page which allows an authenticated attacker to initiate calls and inject messages into channels or direct messages via a malicious webpage or crafted link.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62190
- https://github.com/mattermost/mattermost-plugin-calls/commit/429cfaf2a301a369414d1ca18a3364e85901c8d1
- https://github.com/mattermost/mattermost-plugin-calls
- https://github.com/mattermost/mattermost-plugin-calls/releases/tag/v1.10.0
- https://mattermost.com/security-updates
