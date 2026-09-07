# [H] Jenkins Shortcut Job Plugin stored cross-site scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-jg35-vf67-gg2j
CVE: CVE-2023-40346
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-jg35-vf67-gg2j
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:shortcut-job` — affected >=0 <0.5

## Details
Jenkins Shortcut Job Plugin 0.4 and earlier does not escape the shortcut redirection URL.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to configure shortcut jobs.

Shortcut Job Plugin 0.5 escapes the shortcut redirection URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40346
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-3071
- http://www.openwall.com/lists/oss-security/2023/08/16/3
