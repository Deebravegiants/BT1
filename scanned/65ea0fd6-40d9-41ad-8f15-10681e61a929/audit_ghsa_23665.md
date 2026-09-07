# [M] XSS vulnerability in Jenkins Audit Trail Plugin

## Summary
Severity: Medium
Advisory: GHSA-cj2g-wwfv-mvjh
CVE: CVE-2020-2140
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cj2g-wwfv-mvjh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:audit-trail` — affected >=0 <3.3

## Details
Jenkins Audit Trail Plugin 3.2 and earlier does not escape the error message for the URL Patterns field form validation, resulting in a reflected cross-site scripting vulnerability. Audit Trail Plugin 3.3 escapes the affected part of the error message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2140
- https://github.com/jenkinsci/audit-trail-plugin/commit/40c6d621a03e6a50b291dca7188d07d0aa3de946
- https://github.com/jenkinsci/audit-trail-plugin
- https://jenkins.io/security/advisory/2020-03-09/#SECURITY-1722
- http://www.openwall.com/lists/oss-security/2020/03/09/1
