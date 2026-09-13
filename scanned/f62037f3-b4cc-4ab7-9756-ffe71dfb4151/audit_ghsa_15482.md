# [M] Mattermost fails to strip `embeds` from `metadata` when broadcasting `posted` events

## Summary
Severity: Medium
Advisory: GHSA-59hf-mpf8-pqjh
CVE: CVE-2024-47003
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-09-26
Source: https://github.com/advisories/GHSA-59hf-mpf8-pqjh
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20240806094731-69a8b3df0f9f

## Details
Mattermost does not strip `embeds` from `metadata` when broadcasting `posted` events.

This allows users to include arbitrary embeds in posts, which are then broadcasted via websockets. This can be exploited in many ways, for example to create permalinks with fully customizable content or to trigger a client Side Denial of Service (DoS) by sending a permalink with a non-string message.

The advisory metadata references the appropriate go pseudo version available from pkg.go.dev

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-47003
- https://github.com/mattermost/mattermost/pull/27763
- https://github.com/mattermost/mattermost/commit/69a8b3df0f9fd3a7a5b792ec678b6191618d039b
- https://github.com/c0rydoras/cves/tree/main/CVE-2024-47003
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
