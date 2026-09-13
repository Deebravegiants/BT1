# [M] Mattermost fails to preserve the redacted state of burn-on-read posts during deletion

## Summary
Severity: Medium
Advisory: GHSA-3rhr-jr63-hwq5
CVE: CVE-2026-2578
CWE: CWE-201
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-3rhr-jr63-hwq5
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260127062706-c6b205f0d770
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260127062706-c6b205f0d770
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.1

## Details
Mattermost versions 11.3.x <= 11.3.0 fail to preserve the redacted state of burn-on-read posts during deletion which allows channel members to access unrevealed burn-on-read message contents via the WebSocket post deletion event. Mattermost Advisory ID: MMSA-2026-00579

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2578
- https://github.com/mattermost/mattermost/commit/c6b205f0d77080ef805783de0628b9526af7faec
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
