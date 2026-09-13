# [M] Mattermost Server allows user to get private channel names

## Summary
Severity: Medium
Advisory: GHSA-6mvp-gh77-7vwh
CVE: CVE-2024-10241
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-29
Source: https://github.com/advisories/GHSA-6mvp-gh77-7vwh
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20240813135334-8f3a13122f55

## Details
Mattermost versions 9.5.x <= 9.5.9 fail to properly filter the channel data when ElasticSearch is enabled which allows a user to get private channel names by using cmd+K/ctrl+K.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10241
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
