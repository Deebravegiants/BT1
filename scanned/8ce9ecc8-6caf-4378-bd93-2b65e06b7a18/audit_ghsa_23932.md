# [H] CSRF vulnerability in Jenkins Release plugin

## Summary
Severity: High
Advisory: GHSA-j2h6-j34w-g5vp
CVE: CVE-2018-1000013
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-j2h6-j34w-g5vp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:release` — affected >=0 <2.10

## Details
Jenkins Release Plugin 2.9 and earlier did not require form submissions to be submitted via POST, resulting in a CSRF vulnerability allowing attackers to trigger release builds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000013
- https://jenkins.io/security/advisory/2018-01-22
- http://www.securityfocus.com/bid/102834
