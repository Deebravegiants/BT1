# [H] Mattermost doesn't properly validate msgpack-encoded WebSocket frames before memory allocation

## Summary
Severity: High
Advisory: GHSA-w9m8-p4cc-4qj9
CVE: CVE-2026-5740
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-w9m8-p4cc-4qj9
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.4
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0 <11.4.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.15
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260410202636-17939826efa2

## Details
Mattermost versions 11.6.x <= 11.6.0, 11.5.x <= 11.5.3, 11.4.x <= 11.4.4, 10.11.x <= 10.11.14 fail to properly validate msgpack-encoded WebSocket frames before memory allocation which allows an unauthenticated remote attacker to crash the server process and cause a full service outage for all users via a crafted binary WebSocket message sent to the public WebSocket endpoint.. Mattermost Advisory ID: MMSA-2026-00647

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5740
- https://github.com/mattermost/mattermost/commit/17939826efa20a97f087b3d390ec5136df350bae
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
