# [H] Mattermost Fails to Enforce MFA on Plugin Endpoints

## Summary
Severity: High
Advisory: GHSA-72qv-j8vr-xvfv
CVE: CVE-2025-25068
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-21
Source: https://github.com/advisories/GHSA-72qv-j8vr-xvfv
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.4.0 <10.4.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.3.0 <10.3.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.9
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.5.0 <10.5.1

## Details
Mattermost versions 10.4.x <= 10.4.2, 10.3.x <= 10.3.3, 9.11.x <= 9.11.8, 10.5.x <= 10.5.0 fail to enforce MFA on plugin endpoints, which allows authenticated attackers to bypass MFA protections via API requests to plugin-specific routes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-25068
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
