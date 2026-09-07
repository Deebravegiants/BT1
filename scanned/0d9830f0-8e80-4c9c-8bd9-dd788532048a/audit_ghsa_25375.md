# [H] CSRF vulnerability in Jenkins Translation Assistance plugin

## Summary
Severity: High
Advisory: GHSA-pwvj-6phx-qv8c
CVE: CVE-2018-1000014
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-pwvj-6phx-qv8c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:translation` — affected >=0 <1.16

## Details
Jenkins Translation Assistance Plugin 1.15 and earlier did not require form submissions to be submitted via POST, resulting in a CSRF vulnerability allowing attackers to override localized strings displayed to all users on the current Jenkins instance if the victim is a Jenkins administrator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000014
- https://jenkins.io/security/advisory/2018-01-22
- http://www.securityfocus.com/bid/102809
