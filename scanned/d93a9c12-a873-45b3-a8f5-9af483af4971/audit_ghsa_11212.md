# [M] Mattermost fails to bound memory allocation when processing DOC files

## Summary
Severity: Medium
Advisory: GHSA-xv2p-wchj-qjhp
CVE: CVE-2026-25780
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-xv2p-wchj-qjhp
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260123215601-86797c508c44
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260123215601-86797c508c44
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.1

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 fail to bound memory allocation when processing DOC files which allows an authenticated attacker to cause server memory exhaustion and denial of service via uploading a specially crafted DOC file.. Mattermost Advisory ID: MMSA-2026-00581

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25780
- https://github.com/mattermost/mattermost/commit/86797c508c444e299b20889ce241fde505a402cc
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
