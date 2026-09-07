# [M] Jenkins Build Failure Analyzer Plugin Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2wwh-qgh8-w9xw
CVE: CVE-2023-43502
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-2wwh-qgh8-w9xw
Type: github-advisory

## Affected
- Maven: `com.sonyericsson.jenkins.plugins.bfa:build-failure-analyzer` — affected >=0 <2.4.2

## Details
Jenkins Build Failure Analyzer Plugin 2.4.1 and earlier does not require POST requests for an HTTP endpoint, resulting in cross-site request forgery (CSRF) vulnerabilities.

This vulnerability allows attackers to delete Failure Causes.

Build Failure Analyzer Plugin 2.4.2 requires POST requests for the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43502
- https://github.com/jenkinsci/build-failure-analyzer-plugin/commit/a261229a67c52927d531c48ec0a59bf138ebd4d0
- https://www.jenkins.io/security/advisory/2023-09-20/#SECURITY-3239
- http://www.openwall.com/lists/oss-security/2023/09/20/5
