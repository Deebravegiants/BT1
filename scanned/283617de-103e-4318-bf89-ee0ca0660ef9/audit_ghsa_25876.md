# [M] CSRF vulnerability in Jenkins Release Helper Plugin

## Summary
Severity: Medium
Advisory: GHSA-m4x7-44c8-jg2x
CVE: CVE-2022-27214
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-m4x7-44c8-jg2x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:release-helper` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Release Helper Plugin 1.3.3 and earlier allows attackers to connect to an attacker-specified URL using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27214
- https://github.com/jenkinsci/release-helper-plugin
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2274
- http://www.openwall.com/lists/oss-security/2022/03/15/2
