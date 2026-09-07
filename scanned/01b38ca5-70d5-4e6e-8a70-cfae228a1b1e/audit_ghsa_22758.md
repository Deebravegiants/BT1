# [H] Cross-site request forgery vulnerability in Jenkins XL TestView Plugin

## Summary
Severity: High
Advisory: GHSA-6q4p-jrjv-44gf
CVE: CVE-2019-10386
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6q4p-jrjv-44gf
Type: github-advisory

## Affected
- Maven: `com.xebialabs.xlt.ci:xltestview-plugin` — affected >=0

## Details
A cross-site request forgery vulnerability in Jenkins XL TestView Plugin 1.2.0 and earlier in XLTestView.XLTestDescriptor#doTestConnection allows users with Overall/Read access to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10386
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-1008
- http://www.openwall.com/lists/oss-security/2019/08/07/1
