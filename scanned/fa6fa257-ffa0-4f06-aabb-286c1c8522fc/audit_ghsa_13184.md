# [M] Missing permission checks in Jenkins Frugal Testing Plugin

## Summary
Severity: Medium
Advisory: GHSA-p986-hpr3-493p
CVE: CVE-2023-41947
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-p986-hpr3-493p
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:frugal-testing` — affected >=0

## Details
A missing permission check in Jenkins Frugal Testing Plugin 1.1 and earlier allows attackers with Overall/Read permission to connect to Frugal Testing using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41947
- https://www.jenkins.io/security/advisory/2023-09-06/#SECURITY-3082
- http://www.openwall.com/lists/oss-security/2023/09/06/9
