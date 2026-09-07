# [M] Cross-Site Request Forgery in Jenkins Request Rename Or Delete Plugin

## Summary
Severity: Medium
Advisory: GHSA-qq85-8g89-r5rc
CVE: CVE-2022-34815
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-qq85-8g89-r5rc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rrod` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Request Rename Or Delete Plugin 1.1.0 and earlier allows attackers to accept pending requests, thereby renaming or deleting jobs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34815
- https://github.com/jenkinsci/rrod-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2657
