# [M] Cross-site Scripting in Jenkins Core

## Summary
Severity: Medium
Advisory: GHSA-x3rc-cxv7-6xp6
CVE: CVE-2017-17383
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-x3rc-cxv7-6xp6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.94

## Details
Jenkins through 2.93 allows remote authenticated administrators to conduct XSS attacks via a crafted tool name in a job configuration form, as demonstrated by the JDK tool in Jenkins core and the Ant tool in the Ant plugin, aka SECURITY-624.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17383
- https://jenkins.io/security/advisory/2017-12-05
- http://vsintelli.com/portal/blog/23-security-advisory-2017-12-04
- http://www.securityfocus.com/bid/102130
