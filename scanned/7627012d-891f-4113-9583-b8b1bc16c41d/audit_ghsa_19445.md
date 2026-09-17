# [M] Mattermost vulnerable to Incorrect Implementation of Authentication Algorithm

## Summary
Severity: Medium
Advisory: GHSA-6rqh-8465-2xcw
CVE: CVE-2025-2475
CWE: CWE-303
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-14
Source: https://github.com/advisories/GHSA-6rqh-8465-2xcw
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.5.0 <10.5.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.10
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250220161544-fd356b62b4dd

## Details
Mattermost versions 10.5.x <= 10.5.1, 10.4.x <= 10.4.3, 9.11.x <= 9.11.9 fail to invalidate the cache when a user account is converted to a bot which allows an attacker to login to the bot exactly one time via normal credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2475
- https://github.com/mattermost/mattermost/commit/124547a9ef424431e1e6cf09bdba6c1099d415de
- https://github.com/mattermost/mattermost/commit/40fd60714bd055e00c16301ba6dc0fddfc44e15e
- https://github.com/mattermost/mattermost/commit/88523ceed8a7547c4a4203a30e7c3a8097346280
- https://github.com/mattermost/mattermost/commit/bcd7a4c2bd856dbb40fcda227b363fa5f6f548a7
- https://github.com/mattermost/mattermost/commit/fd356b62b4dd3318d2c8019d2310abdd6ce24c8c
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- https://pkg.go.dev/vuln/GO-2025-3610
