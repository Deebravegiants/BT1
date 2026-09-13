# [M] Mattermost allows team admin user without "Add Team Members" permission to disable invite URL

## Summary
Severity: Medium
Advisory: GHSA-3j95-8g47-fpwh
CVE: CVE-2024-40884
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-08-22
Source: https://github.com/advisories/GHSA-3j95-8g47-fpwh
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.5.0 <9.5.8
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.10.0 <9.10.1

## Details
Mattermost versions 9.5.x <= 9.5.7, 9.10.x <= 9.10.0 fail to properly enforce permissions which allows a team admin user without "Add Team Members" permission to disable the invite URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-40884
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
