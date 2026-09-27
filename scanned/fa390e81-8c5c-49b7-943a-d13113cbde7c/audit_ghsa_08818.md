# [M] Mattermost doesn't prevent disclosure of created user password

## Summary
Severity: Medium
Advisory: GHSA-wvgv-4fc3-2rcp
CVE: CVE-2026-6345
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-wvgv-4fc3-2rcp
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.5.0 <11.5.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.11.0 <10.11.14
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0 <11.4.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260311102650-3057ae7e83e9
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260311102650-3057ae7e83e9

## Details
Mattermost versions 11.5.x <= 11.5.1, 10.11.x <= 10.11.13, 11.4.x <= 11.4.3 doesn't prevent disclosure of created user password which allows a malicious attacker to impersonate a user via the use of some of those passwords.. Mattermost Advisory ID: MMSA-2026-00614

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6345
- https://github.com/mattermost/mattermost/commit/3057ae7e83e9c827ce7818d67c0f3a208f0d9709
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
