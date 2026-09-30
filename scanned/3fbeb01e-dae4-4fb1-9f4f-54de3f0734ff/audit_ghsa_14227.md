# [M] Jenkins Thycotic Secret Server Plugin missing permissions check

## Summary
Severity: Medium
Advisory: GHSA-4697-3g92-gh78
CVE: CVE-2023-30518
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-4697-3g92-gh78
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:thycotic-secret-server` — affected >=0

## Details
Jenkins Thycotic Secret Server Plugin 1.0.2 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30518
- https://www.jenkins.io/security/advisory/2023-04-12/#SECURITY-2837
- http://www.openwall.com/lists/oss-security/2023/04/13/3
