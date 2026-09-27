# [M] Mattermost doesn't verify channel membership when processing AI-assisted message rewrites

## Summary
Severity: Medium
Advisory: GHSA-8r89-8w26-cq32
CVE: CVE-2026-5163
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-8r89-8w26-cq32
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.5.0 <11.5.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260401090745-f4d1abe7e8f5
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260401090745-f4d1abe7e8f5

## Details
Mattermost versions 11.5.x <= 11.5.1 fail to verify channel membership when processing AI-assisted message rewrites which allows an authenticated attacker to read the content of threads in private channels and direct messages they do not have access to via a crafted request to the post rewrite endpoint.. Mattermost Advisory ID: MMSA-2026-00645

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5163
- https://github.com/mattermost/mattermost/commit/f4d1abe7e8f545f1a87f463fa9fe451c731aebf8
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
