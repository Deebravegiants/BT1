# [M] Mattermost doesn't check the create_post channel permission during post edit operations

## Summary
Severity: Medium
Advisory: GHSA-v549-xx3c-6pc8
CVE: CVE-2026-3637
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-v549-xx3c-6pc8
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.11.0 <10.11.14
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0 <11.4.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260316171743-090408f09f53
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.5.0 <11.5.2
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260316171743-090408f09f53

## Details
Mattermost versions 11.5.x <= 11.5.1, 10.11.x <= 10.11.13, 11.4.x <= 11.4.3 fail to check the create_post channel permission during post edit operations which allows an authenticated attacker with revoked posting privileges to modify their existing posts via direct API requests to the post update and patch endpoints.. Mattermost Advisory ID: MMSA-2026-00627

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3637
- https://github.com/mattermost/mattermost/commit/090408f09f53ffc9afc6c65c7c7c1fd3a8cd22f3
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
