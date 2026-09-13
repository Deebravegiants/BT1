# [M] Mattermost Desktop App Uncontrolled Search Path Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wj4j-qc2m-fgh7
CVE: CVE-2024-39613
CWE: CWE-427
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-09-16
Source: https://github.com/advisories/GHSA-wj4j-qc2m-fgh7
Type: github-advisory

## Affected
- npm: `mattermost-desktop` — affected >=0 <5.9.0

## Details
Mattermost Desktop App versions <=5.8.0 fail to specify an absolute path when searching the cmd.exe file, which allows a local attacker who is able to put an cmd.exe file in the Downloads folder of a user's machine to cause remote code execution on that machine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39613
- https://docs.mattermost.com/about/desktop-app-changelog.html
- https://github.com/mattermost/desktop
- https://mattermost.com/security-updates
