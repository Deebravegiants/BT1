# [M] Mattermost: Authenticated DoS through failure to prevent rendering of external SVGs on link embeds 

## Summary
Severity: Medium
Advisory: GHSA-86vc-mg26-fj6x
CVE: CVE-2026-20719
CWE: CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-86vc-mg26-fj6x
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0-rc1 <11.4.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.3.0-rc1 <11.3.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.2.0-rc1 <11.2.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20260105080200-d27a2195068d <8.0.0-20260217110922-b7d4a1f1f59b
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.11.0-rc1 <10.11.2

## Details
Mattermost versions 11.4.x <= 11.4.0, 11.3.x <= 11.3.1, 11.2.x <= 11.2.3, 10.11.x <= 10.11.11 fail to prevent rendering of external SVGs on link embeds which allows unauthenticated users to crash the Mattermost webapp and desktop app via creating an issue or PR on GitHub. Mattermost Advisory ID: MMSA-2026-00595

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-20719
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
