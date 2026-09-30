# [M] Mattermost Desktop App fails to safeguard screen capture functionality

## Summary
Severity: Medium
Advisory: GHSA-5777-rcjj-9p22
CVE: CVE-2024-39772
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-09-16
Source: https://github.com/advisories/GHSA-5777-rcjj-9p22
Type: github-advisory

## Affected
- npm: `mattermost-desktop` — affected >=0 <5.9.0

## Details
Mattermost Desktop App versions <=5.8.0 fail to safeguard screen capture functionality which allows an attacker to silently capture high-quality screenshots via JavaScript APIs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39772
- https://github.com/mattermost/desktop
- https://mattermost.com/security-updates
