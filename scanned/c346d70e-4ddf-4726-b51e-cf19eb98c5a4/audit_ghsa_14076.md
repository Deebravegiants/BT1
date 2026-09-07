# [H] Jenkins LoadComplete support Plugin Cross-site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-7p6g-gr9g-vfx6
CVE: CVE-2023-33007
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-7p6g-gr9g-vfx6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:loadcomplete` — affected >=0

## Details
Jenkins LoadComplete support Plugin 1.0 and earlier does not escape the LoadComplete test name in its test result page.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33007
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-2903
