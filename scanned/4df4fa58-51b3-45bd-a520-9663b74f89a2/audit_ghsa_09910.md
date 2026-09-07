# [M] Mattermost doesn't validate CSRF tokens on an authentication endpoint

## Summary
Severity: Medium
Advisory: GHSA-m7cf-4gh2-v4qg
CVE: CVE-2026-28741
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-m7cf-4gh2-v4qg
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20250721062209-4952acea88ce <8.0.0-20260220133927-c29cf05d40f8
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.5.0-rc1 <11.5.0
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0-rc1 <11.4.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.3.0-rc1 <11.3.3

## Details
Mattermost versions 10.11.x <= 10.11.12, 11.5.x <= 11.5.0, 11.4.x <= 11.4.2, 11.3.x <= 11.3.2 fail to validate CSRF tokens on an authentication endpoint which allows an attacker to update a user's authentication method via a CSRF attack by tricking a user into visiting a malicious page. Mattermost Advisory ID: MMSA-2026-00625.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-28741
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
