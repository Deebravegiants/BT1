# [M] Mattermost doesn't validate the X-Requested-With header on the burn-on-read reveal endpoint

## Summary
Severity: Medium
Advisory: GHSA-xvcx-mgpc-5xh3
CVE: CVE-2026-6339
CWE: CWE-346
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-xvcx-mgpc-5xh3
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.5.0 <11.5.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0 <11.4.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260327001745-7a339a6438f5
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260327001745-7a339a6438f5

## Details
Mattermost versions 11.5.x <= 11.5.1, 11.4.x <= 11.4.3 fail to validate the X-Requested-With header on the burn-on-read reveal endpoint which allows an authenticated channel member to force the reveal of a burn-on-read message without recipient consent via a crafted Markdown image tag.. Mattermost Advisory ID: MMSA-2026-00636

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6339
- https://github.com/mattermost/mattermost/commit/7a339a6438f5a4a5feba6b8de887f17a1378b207
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
