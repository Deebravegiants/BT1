# [M] Jenkins Codefresh Integration Plugin Improper Certificate Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-862j-cv9p-6hpf
CVE: CVE-2019-10381
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-862j-cv9p-6hpf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:codefresh` — affected >=0

## Details
Codefresh Integration Plugin unconditionally disables SSL/TLS certificate validation for the entire Jenkins controller JVM.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10381
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-931
- http://www.openwall.com/lists/oss-security/2019/08/07/1
