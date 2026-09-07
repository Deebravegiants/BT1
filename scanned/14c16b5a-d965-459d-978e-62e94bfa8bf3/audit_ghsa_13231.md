# [M] Jenkins Build Failure Analyzer Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-55q6-r3hm-7ff4
CVE: CVE-2023-43501
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-55q6-r3hm-7ff4
Type: github-advisory

## Affected
- Maven: `com.sonyericsson.jenkins.plugins.bfa:build-failure-analyzer` — affected >=0 <2.4.2

## Details
Jenkins Build Failure Analyzer Plugin 2.4.1 and earlier does not perform a permission check in a connection test HTTP endpoint.

This allows attackers with Overall/Read permission to connect to an attacker-specified hostname and port using attacker-specified username and password.

Additionally, this HTTP endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

Build Failure Analyzer Plugin 2.4.2 requires POST requests and Overall/Administer permission for the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43501
- https://github.com/jenkinsci/build-failure-analyzer-plugin/commit/a261229a67c52927d531c48ec0a59bf138ebd4d0
- https://www.jenkins.io/security/advisory/2023-09-20/#SECURITY-3226
- http://www.openwall.com/lists/oss-security/2023/09/20/5
