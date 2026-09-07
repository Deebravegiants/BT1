# [H] Cross-Site Request Forgery in Jenkins P4 Plugin

## Summary
Severity: High
Advisory: GHSA-3rj3-qp2j-4fj2
CVE: CVE-2021-21655
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-3rj3-qp2j-4fj2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:p4` — affected >=0 <1.11.5

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins P4 Plugin 1.11.4 and earlier allows attackers to connect to an attacker-specified Perforce server using attacker-specified username and password.

Jenkins P4 Plugin 1.11.5 requires POST requests for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21655
- https://github.com/jenkinsci/p4-plugin/commit/6b0237b04c985987460e31987d3cb314afa1ead6
- https://github.com/jenkinsci/p4-plugin
- https://www.jenkins.io/security/advisory/2021-05-11/#SECURITY-2327
