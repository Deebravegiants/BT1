# [M] Jenkins Compuware Strobe Measurement Plugin Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hcw3-6459-pwhc
CVE: CVE-2022-43431
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-hcw3-6459-pwhc
Type: github-advisory

## Affected
- Maven: `com.compuware.jenkins:compuware-strobe-measurement` — affected >=0 <1.0.2

## Details
Jenkins Compuware Strobe Measurement Plugin 1.0.1 and earlier does not perform a permission check in an HTTP endpoint, allowing attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43431
- https://github.com/jenkinsci/compuware-strobe-measurement-plugin/commit/29a0d38d12e31ff8538473742c05a2e11f15c0df
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2631
- http://www.openwall.com/lists/oss-security/2022/10/19/3
