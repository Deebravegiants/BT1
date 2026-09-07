# [M] Mattermost Desktop App Remote Code Execution

## Summary
Severity: Medium
Advisory: GHSA-hvxg-77mg-vrvp
CVE: CVE-2024-37182
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-14
Source: https://github.com/advisories/GHSA-hvxg-77mg-vrvp
Type: github-advisory

## Affected
- npm: `mattermost-desktop` — affected >=0 <5.8.0

## Details
Mattermost Desktop App versions <=5.7.0 fail to correctly prompt for permission when opening external URLs which allows a remote attacker to force a victim over the Internet to run arbitrary programs on the victim's system via custom URI schemes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37182
- https://github.com/mattermost/desktop/commit/1c9fc719dc2b74495a05f7ebc90e92e7daa03e6d
- https://github.com/mattermost/desktop
- https://mattermost.com/security-updates
