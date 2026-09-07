# [H] Jenkins Project Inheritance Plugin vulnerable to cross site scripting

## Summary
Severity: High
Advisory: GHSA-3hx4-285w-v6mm
CVE: CVE-2022-34787
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-3hx4-285w-v6mm
Type: github-advisory

## Affected
- Maven: `hudson.plugins:project-inheritance` — affected >=0

## Details
Jenkins Project Inheritance Plugin 21.04.03 and earlier does not escape the reason a build is blocked in tooltips, resulting in a cross-site scripting (XSS) vulnerability exploitable by attackers able to control the reason a queue item is blocked.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34787
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-1919
