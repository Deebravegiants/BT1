# [M] Passwords transmitted in plain text by Jenkins ReadyAPI Functional Testing Plugin

## Summary
Severity: Medium
Advisory: GHSA-q4qq-8q2r-g2f2
CVE: CVE-2020-2251
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q4qq-8q2r-g2f2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:soapui-pro-functional-testing` — affected >=0 <1.6

## Details
ReadyAPI Functional Testing Plugin stores project passwords in job `config.xml` files on the Jenkins controller as part of its configuration.

While these passwords are stored encrypted on disk since ReadyAPI Functional Testing Plugin 1.4, they are transmitted in plain text as part of the global configuration form by ReadyAPI Functional Testing Plugin 1.5 and earlier. These passwords can be viewed by attackers with Extended Read permission.

This only affects Jenkins before 2.236, including 2.235.x LTS, as Jenkins 2.236 introduces a security hardening that transparently encrypts and decrypts data used for a Jenkins password form field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2251
- https://github.com/jenkinsci/soapui-pro-functional-testing-plugin
- https://jenkins.io/security/advisory/2020-09-01/#SECURITY-1631%20(2)
- http://www.openwall.com/lists/oss-security/2020/09/01/3
