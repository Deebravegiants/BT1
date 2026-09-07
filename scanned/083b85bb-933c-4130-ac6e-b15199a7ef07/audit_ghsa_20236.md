# [M] Cross-Site Request Forgery in Jenkins Beaker builder Plugin

## Summary
Severity: Medium
Advisory: GHSA-vqpp-q5x5-qj4r
CVE: CVE-2022-34207
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-vqpp-q5x5-qj4r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:beaker-builder` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Beaker builder Plugin 1.10 and earlier allows attackers to connect to an attacker-specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34207
- https://github.com/jenkinsci/beaker-builder-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2248
