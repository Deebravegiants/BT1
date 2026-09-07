# [M] Jenkins Test Results Aggregator Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-h656-vmrg-7rr6
CVE: CVE-2023-37956
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-h656-vmrg-7rr6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:test-results-aggregator` — affected >=0

## Details
Jenkins Test Results Aggregator Plugin 1.2.13 and earlier does not perform a permission check in an HTTP endpoint implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified username and password.

Additionally, this HTTP endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37956
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3122
- http://www.openwall.com/lists/oss-security/2023/07/12/2
