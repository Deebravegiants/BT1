# [M] Jenkins OWASP Dependency-Check Plugin has stored XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9pp4-mx6x-xh36
CVE: CVE-2024-28153
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-9pp4-mx6x-xh36
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:dependency-check-jenkins-plugin` — affected >=0 <5.4.6

## Details
Jenkins OWASP Dependency-Check Plugin 5.4.5 and earlier does not escape vulnerability metadata from Dependency-Check reports, resulting in a stored cross-site scripting (XSS) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28153
- https://github.com/jenkinsci/dependency-check-plugin/commit/b3b286a9615603f0294eb740193d153d843fae3a
- https://github.com/jenkinsci/dependency-check-plugin
- https://www.jenkins.io/security/advisory/2024-03-06/#SECURITY-3344
- http://www.openwall.com/lists/oss-security/2024/03/06/3
