# [M] Mattermost Server's OAuth 2.0 service is vulnerable to attack through Missing Authorization

## Summary
Severity: Medium
Advisory: GHSA-hgrp-fgm8-56g8
CVE: CVE-2017-18872
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hgrp-fgm8-56g8
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.3.3
- Go: `github.com/mattermost/mattermost-server` — affected >=4.4.0-rc1 <4.4.3

## Details
An issue was discovered in Mattermost Server before 4.4.3 and 4.3.3. Attackers could reconfigure an OAuth app in some cases where Mattermost is an OAuth 2.0 service provider.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18872
- https://github.com/mattermost/mattermost/commit/8f6bb1570dd234c63de5241eff9fbb268aad358c
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
- http://github.com/mattermost/mattermost/commit/753386c2b2b06233d8bd977e3db29a4fe18098cb
