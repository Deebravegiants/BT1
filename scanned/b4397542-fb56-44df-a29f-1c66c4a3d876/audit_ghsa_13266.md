# [H] Jenkins Benchmark Evaluator Plugin vulnerable to cross-site request forgery

## Summary
Severity: High
Advisory: GHSA-wgvx-9rh5-4g4m
CVE: CVE-2023-37962
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-wgvx-9rh5-4g4m
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:benchmark-evaluator` — affected >=0

## Details
Jenkins Benchmark Evaluator Plugin 1.0.1 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL and to check for the existence of directories, `.csv`, and `.ycsb` files on the Jenkins controller file system.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37962
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3119
- http://www.openwall.com/lists/oss-security/2023/07/12/2
