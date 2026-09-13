# [M] Mattermost does not verify remote cluster channel access when processing shared channel membership removals

## Summary
Severity: Medium
Advisory: GHSA-8h9w-w78c-vvr3
CVE: CVE-2026-28759
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-8h9w-w78c-vvr3
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.5.0 <11.5.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.11.0 <10.11.14
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0 <11.4.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260216150504-8738f8c4b3d4
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260216150504-8738f8c4b3d4

## Details
Mattermost versions 11.5.x <= 11.5.1, 10.11.x <= 10.11.13, 11.4.x <= 11.4.3 fail to validate that a remote cluster has access to a channel before processing membership removal requests during shared channel membership sync, which allows a malicious remote cluster to remove any user from any channel, including private channels, via crafted membership sync messages targeting channels the remote cluster is not authorized to access. Mattermost Advisory ID: MMSA-2026-00576.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-28759
- https://github.com/mattermost/mattermost/commit/8738f8c4b3d42b2b687a6231e72f313357a2e891
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
