# [M] Mattermost vulnerable to excessive memory consumption

## Summary
Severity: Medium
Advisory: GHSA-w496-f5qq-m58j
CVE: CVE-2023-5969
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-11-06
Source: https://github.com/advisories/GHSA-w496-f5qq-m58j
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server/v6` — affected >=0 <7.8.12
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0 <8.0.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.1.0 <8.1.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.0.0 <9.0.1

## Details
Mattermost fails to properly sanitize the request to `/api/v4/redirect_location` allowing an attacker, sending a specially crafted request to `/api/v4/redirect_location`, to fill up the memory due to caching large items.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5969
- https://github.com/mattermost/mattermost/pull/24429
- https://github.com/mattermost/mattermost/commit/77f094c7ee8c7a00be01c2df72f948a62c690b66
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
