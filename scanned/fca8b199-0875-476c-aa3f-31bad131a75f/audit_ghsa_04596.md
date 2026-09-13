# [M] Mattermost doesn't restrict role_updated websocket event broadcasts to members of the affected team or channel

## Summary
Severity: Medium
Advisory: GHSA-rp4v-qc77-phm4
CVE: CVE-2026-3433
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-rp4v-qc77-phm4
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.17
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20250731163400-5b955468ea1e <8.0.0-20260504071740-9408b98025d7

## Details
Mattermost versions 11.6.x <= 11.6.1, 11.5.x <= 11.5.4, 10.11.x <= 10.11.15, 10.11.x <= 10.11.16 fail to restrict role_updated websocket event broadcasts to members of the affected team or channel, which allows an authenticated attacker with guest-level access to observe permission scheme change notifications for private teams they are not a member of via the websocket connection. Mattermost Advisory ID: MMSA-2026-00616

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3433
- https://github.com/mattermost/mattermost/pull/35497
- https://github.com/mattermost/mattermost/pull/36256
- https://github.com/mattermost/mattermost/pull/36257
- https://github.com/mattermost/mattermost/pull/36341
- https://github.com/mattermost/mattermost/commit/0a0ab0d54d899d308bd1352cc577036917500318
- https://github.com/mattermost/mattermost/commit/7425c6817bf244f976c729f8a73cecac8039a1e1
- https://github.com/mattermost/mattermost/commit/9408b98025d7364d7dfe7cdb28fcd109b1b595a6
- https://github.com/mattermost/mattermost/commit/a30a331a29b9766d46716d4252056d7b74e66da0
- https://github.com/mattermost/mattermost
- https://github.com/mattermost/mattermost/releases/tag/v10.11.16
- https://github.com/mattermost/mattermost/releases/tag/v11.5.5
- https://github.com/mattermost/mattermost/releases/tag/v11.6.2
- https://github.com/mattermost/mattermost/releases/tag/v11.7.0
- https://mattermost.com/security-updates
