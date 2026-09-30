# [M] Missing permission checks in Jenkins Release Helper Plugin

## Summary
Severity: Medium
Advisory: GHSA-p9gq-76fj-4p4p
CVE: CVE-2022-27215
CWE: CWE-281, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-p9gq-76fj-4p4p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:release-helper` — affected >=0

## Details
A missing permission check in Jenkins Release Helper Plugin 1.3.3 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27215
- https://github.com/jenkinsci/release-helper-plugin
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2274
- http://www.openwall.com/lists/oss-security/2022/03/15/2
