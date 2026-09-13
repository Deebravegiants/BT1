# [M] Missing permission check in Jenkins BearyChat Plugin

## Summary
Severity: Medium
Advisory: GHSA-67w4-w877-jv29
CVE: CVE-2023-24459
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-67w4-w877-jv29
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:bearychat` — affected >=0

## Details
A missing permission check in Jenkins BearyChat Plugin 3.0.2 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24459
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2745
