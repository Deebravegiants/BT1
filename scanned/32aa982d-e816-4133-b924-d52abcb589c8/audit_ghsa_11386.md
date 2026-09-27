# [M] Mattermost allows attackers to take over arbitrary user accounts via overly permissive substring matching flaw

## Summary
Severity: Medium
Advisory: GHSA-fg35-5rf6-qg3g
CVE: CVE-2026-27656
CWE: CWE-303
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-fg35-5rf6-qg3g
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0-rc1 <11.4.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.2
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.4
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.12
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20260105080200-d27a2195068d <8.0.0-20260217110922-b7d4a1f1f59b

## Details
Mattermost versions 11.4.x <= 11.4.0, 11.3.x <= 11.3.1, 11.2.x <= 11.2.3, 10.11.x <= 10.11.11 fail to properly validate user identity in the OpenID {{IsSameUser()}} comparison logic, which allows an attacker to take over arbitrary user accounts via an overly permissive substring matching flaw in the user discovery flow. Mattermost Advisory ID: MMSA-2026-00590

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27656
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
