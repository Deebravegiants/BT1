# [M] Jenkins JUnit Plugin CSRF vulnerability

## Summary
Severity: Medium
Advisory: GHSA-x9gm-m8pp-54vx
CVE: CVE-2018-1000411
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-x9gm-m8pp-54vx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:junit` — affected >=0 <1.26

## Details
A cross-site request forgery vulnerability exists in Jenkins JUnit Plugin 1.25 and earlier in TestObject.java that allows setting the description of a test result.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000411
- https://github.com/jenkinsci/junit-plugin/commit/091ee0dc8dd6023713827ce1a5914fa9fa9b6043
- https://github.com/jenkinsci/junit-plugin
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-1101
- https://web.archive.org/web/20200227092927/http://www.securityfocus.com/bid/106532
