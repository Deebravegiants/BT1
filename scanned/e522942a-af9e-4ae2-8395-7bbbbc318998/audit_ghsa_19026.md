# [C] Mattermost fails to properly validate OAuth state tokens during OpenID Connect authentication

## Summary
Severity: Critical
Advisory: GHSA-3x39-62h4-f8j6
CVE: CVE-2025-12419
CWE: CWE-287, CWE-303
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-27
Source: https://github.com/advisories/GHSA-3x39-62h4-f8j6
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20251028000919-d3ed703dc833
- Go: `github.com/mattermost/mattermost-server` — affected >=10.12.0 <10.12.2
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.5.0 <10.5.13
- Go: `github.com/mattermost/mattermost-server` — affected >=11.0.0 <11.0.4

## Details
Mattermost versions 10.12.x <= 10.12.1, 10.11.x <= 10.11.4, 10.5.x <= 10.5.12, 11.0.x <= 11.0.3 fail to properly validate OAuth state tokens during OpenID Connect authentication which allows an authenticated attacker with team creation privileges to take over a user account via manipulation of authentication data during the OAuth completion flow. This requires email verification to be disabled (default: disabled), OAuth/OpenID Connect to be enabled, and the attacker to control two users in the SSO system with one of them never having logged into Mattermost.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12419
- https://github.com/mattermost/mattermost/pull/34296
- https://github.com/mattermost/mattermost/commit/15364790cc277cfaa372693d2d5442b87f70fd42
- https://github.com/mattermost/mattermost/commit/364c2203de00fe0d8424b6b46d6f0eeb02a2539a
- https://github.com/mattermost/mattermost/commit/46b5c436bb3093cc1da3fa2455f93d4c52389eee
- https://github.com/mattermost/mattermost/commit/c3f4818afe46a7084740e809708ae22641c76d8d
- https://github.com/mattermost/mattermost/commit/d3ed703dc8330684952eb8d49a375bac6ea7b0c6
- https://github.com/advisories/GHSA-3x39-62h4-f8j6
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
