# [M] Jenkins Report Portal Plugin missing permissions check

## Summary
Severity: Medium
Advisory: GHSA-c9jf-rhvg-p65r
CVE: CVE-2023-30526
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-c9jf-rhvg-p65r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:reportportal` — affected >=0

## Details
Jenkins Report Portal Plugin 0.5 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified bearer token authentication.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30526
- https://www.jenkins.io/security/advisory/2023-04-12/#SECURITY-2950
- http://www.openwall.com/lists/oss-security/2023/04/13/3
