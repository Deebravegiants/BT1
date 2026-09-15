# [M] Mattermost has an Invite Token Replay Vulnerability via Channel Membership Manipulation

## Summary
Severity: Medium
Advisory: GHSA-x3r8-2hmh-89f5
CVE: CVE-2025-13324
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-12-17
Source: https://github.com/advisories/GHSA-x3r8-2hmh-89f5
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost` — affected >=10.12.0 <10.12.2
- Go: `github.com/mattermost/mattermost` — affected >=10.11.0-rc1 <10.11.5
- Go: `github.com/mattermost/mattermost` — affected >=11.0.0-alpha.1 <11.0.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20251031095924-e7e23b94e006
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <11.0.4

## Details
Mattermost versions 10.11.x < 10.11.5, 11.0.x < 11.0.4, 10.12.x < 10.12.2 fail to invalidate remote cluster invite tokens when using the legacy (version 1) protocol or when the confirming party does not provide a refreshed token, which allows an attacker who has obtained an invite token to authenticate as the remote cluster and perform limited actions on shared channels even after the invitation has been legitimately confirmed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13324
- https://github.com/mattermost/mattermost/commit/364c2203de00fe0d8424b6b46d6f0eeb02a2539a
- https://github.com/mattermost/mattermost/commit/7ccb62db7958abd6a4b21a06c5a4f5367a8f8b1f
- https://github.com/mattermost/mattermost/commit/9f54e5cdc3aef412945ff0e6a58338f7b549bdda
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
