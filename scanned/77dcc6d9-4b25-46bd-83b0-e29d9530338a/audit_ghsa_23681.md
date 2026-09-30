# [H] Jenkins TAP Plugin allows Path Traversal

## Summary
Severity: High
Advisory: GHSA-24jc-w55j-5p83
CVE: CVE-2016-4986
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-24jc-w55j-5p83
Type: github-advisory

## Affected
- Maven: `org.tap4j:tap` — affected >=0 <1.25

## Details
Directory traversal vulnerability in the TAP plugin before 1.25 in Jenkins allows remote attackers to read arbitrary files via an unspecified parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4986
- https://github.com/jenkinsci/tap-plugin/commit/8e2a3aa86ce57a98c69e6038e15ae8fe47d08124
- https://github.com/jenkinsci/tap-plugin
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-06-20
