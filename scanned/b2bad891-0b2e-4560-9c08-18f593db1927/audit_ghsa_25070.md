# [M] Inefficient Regular Expression Complexity in Jenkins Build Failure Analyzer Plugin

## Summary
Severity: Medium
Advisory: GHSA-2hhc-f86x-x74f
CVE: CVE-2019-16555
CWE: CWE-1333, CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2hhc-f86x-x74f
Type: github-advisory

## Affected
- Maven: `com.sonyericsson.jenkins.plugins.bfa:build-failure-analyzer` — affected >=0 <1.24.2

## Details
A user-supplied regular expression in Jenkins Build Failure Analyzer Plugin 1.24.1 and earlier was processed in a way that wasn't interruptible, allowing attackers to have Jenkins evaluate a regular expression without the ability to interrupt this process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16555
- https://github.com/jenkinsci/build-failure-analyzer-plugin/commit/f316c885552ac75289cbb11b2af5757f18784bcb
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1651
- http://www.openwall.com/lists/oss-security/2019/12/17/1
