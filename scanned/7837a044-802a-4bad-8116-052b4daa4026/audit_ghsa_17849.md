# [M] Jenkins Zoom Plugin Stores Sensitive Information in Cleartext

## Summary
Severity: Medium
Advisory: GHSA-jx45-xp6q-cwjc
CVE: CVE-2025-0142
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-01-30
Source: https://github.com/advisories/GHSA-jx45-xp6q-cwjc
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:zoom` — affected >=0 <1.4

## Details
Cleartext storage of sensitive information in the Zoom Jenkins Marketplace plugin before version 1.4 may allow an authenticated user to conduct a disclosure of information via network access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-0142
- https://github.com/jenkinsci/zoom-plugin
- https://www.zoom.com/en/trust/security-bulletin/zsb-25001
