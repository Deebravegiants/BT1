# [M] Mattermost makes Use of Weak Hash

## Summary
Severity: Medium
Advisory: GHSA-9p92-x77w-9fw2
CVE: CVE-2025-9078
CWE: CWE-328
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-9p92-x77w-9fw2
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=10.8.0 <10.8.4
- Go: `github.com/mattermost/mattermost-server` — affected >=10.5.0 <10.5.9
- Go: `github.com/mattermost/mattermost-server` — affected >=9.11.0 <9.11.18
- Go: `github.com/mattermost/mattermost-server` — affected >=10.10.0 <10.10.2
- Go: `github.com/mattermost/mattermost-server` — affected >=10.9.0 <10.9.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250718075842-cd87e5c87737

## Details
Mattermost versions 10.8.x <= 10.8.3, 10.5.x <= 10.5.8, 9.11.x <= 9.11.17, 10.10.x <= 10.10.1, 10.9.x <= 10.9.3 fail to properly validate cache keys for link metadata which allows authenticated users to access unauthorized posts and poison link previews via hash collision attacks on FNV-1 hashing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-9078
- https://github.com/mattermost/mattermost/commit/356880c8430b77a4a390c89d5a33f6928188d137
- https://github.com/mattermost/mattermost/commit/944ad5cdd9876ef61c78c8275906262a4118755a
- https://github.com/mattermost/mattermost/commit/a8a4badc130be101e5bc4b7916bbcd2f966c4b79
- https://github.com/mattermost/mattermost/commit/cd87e5c877373f109742aa90a3fa136c14774325
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
