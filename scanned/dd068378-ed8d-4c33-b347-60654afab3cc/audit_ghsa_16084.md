# [M] Missing permission check in Jenkins Script Security Plugin 

## Summary
Severity: Medium
Advisory: GHSA-jv82-75fh-23r7
CVE: CVE-2024-52549
CWE: CWE-306, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-jv82-75fh-23r7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1368.vb

## Details
Jenkins Script Security Plugin 1367.vdf2fc45f229c and earlier, except 1365.1367.va_3b_b_89f8a_95b_ and 1362.1364.v4cf2dc5d8776, does not perform a permission check in a method implementing form validation, allowing attackers with Overall/Read permission to check for the existence of files on the controller file system. This allows attackers with Overall/Read permission to check for the existence of files on the controller file system. Script Security Plugin 1368.vb_b_402e3547e7 requires Overall/Administer permission for the affected form validation method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52549
- https://github.com/jenkinsci/script-security-plugin
- https://www.jenkins.io/security/advisory/2024-11-13/#SECURITY-3447
