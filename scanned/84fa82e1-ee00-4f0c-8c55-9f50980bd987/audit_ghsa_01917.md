# [M] Missing Authorization in Jenkins P4 plugin

## Summary
Severity: Medium
Advisory: GHSA-h6qv-f5gf-8gcf
CVE: CVE-2021-21654
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-h6qv-f5gf-8gcf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:p4` — affected >=0 <1.11.5

## Details
Jenkins P4 Plugin 1.11.4 and earlier does not perform permission checks in multiple HTTP endpoints, allowing attackers with Overall/Read permission to connect to an attacker-specified Perforce server using attacker-specified username and password.

Jenkins P4 Plugin 1.11.5 requires Overall/Administer for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21654
- https://github.com/jenkinsci/p4-plugin/commit/6b0237b04c985987460e31987d3cb314afa1ead6
- https://github.com/jenkinsci/p4-plugin
- https://www.jenkins.io/security/advisory/2021-05-11/#SECURITY-2327
