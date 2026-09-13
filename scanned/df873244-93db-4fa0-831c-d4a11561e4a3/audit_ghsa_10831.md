# [H] Mattermost allows attackers to manipulate administrator terminals via crafted messages containing ANSI and OSC escape sequences

## Summary
Severity: High
Advisory: GHSA-3439-vqgj-2gcf
CVE: CVE-2026-3108
CWE: CWE-150
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-3439-vqgj-2gcf
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0-rc1 <11.4.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.3.0-rc1 <11.3.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20260105080200-d27a2195068d <8.0.0-20260217110922-b7d4a1f1f59b

## Details
Mattermost versions 11.2.x <= 11.2.2, 10.11.x <= 10.11.10, 11.4.x <= 11.4.0, 11.3.x <= 11.3.1 fail to sanitize user-controlled post content in the mmctl commands terminal output which allows attackers to manipulate administrator terminals via crafted messages containing ANSI and OSC escape sequences that enable screen manipulation, fake prompts, and clipboard hijacking. Mattermost Advisory ID: MMSA-2026-00599.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3108
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
