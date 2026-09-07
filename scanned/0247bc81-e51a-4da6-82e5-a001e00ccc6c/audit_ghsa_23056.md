# [M] Jenkins VMware Lab Manager Slaves Plugin vulnerable to Improper Certificate Validation

## Summary
Severity: Medium
Advisory: GHSA-jxg7-cghf-mggx
CVE: CVE-2019-10382
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jxg7-cghf-mggx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:labmanager` — affected >=0

## Details
VMware Lab Manager Slaves Plugin unconditionally disables SSL/TLS certificate validation for the entire Jenkins controller JVM.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10382
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-1376
- http://www.openwall.com/lists/oss-security/2019/08/07/1
