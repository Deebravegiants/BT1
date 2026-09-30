# [M] Missing permission checks in Jenkins CONS3RT Plugin allow enumerating credentials IDs

## Summary
Severity: Medium
Advisory: GHSA-p37p-wg92-2fc4
CVE: CVE-2022-41252
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-p37p-wg92-2fc4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cons3rt` — affected >=0

## Details
CONS3RT Plugin 1.0.0 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41252
- https://github.com/jenkinsci/cons3rt-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2752
- http://www.openwall.com/lists/oss-security/2022/09/21/5
