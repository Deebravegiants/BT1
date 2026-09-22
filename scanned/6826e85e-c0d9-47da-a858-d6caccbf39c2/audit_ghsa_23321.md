# [M] Missing permission check in Jenkins XL TestView Plugin

## Summary
Severity: Medium
Advisory: GHSA-vf2c-w49g-3xf3
CVE: CVE-2019-10387
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vf2c-w49g-3xf3
Type: github-advisory

## Affected
- Maven: `com.xebialabs.xlt.ci:xltestview-plugin` — affected >=0

## Details
A missing permission check in Jenkins XL TestView Plugin 1.2.0 and earlier in XLTestView.XLTestDescriptor#doTestConnection allows users with Overall/Read access to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10387
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-1008
- http://www.openwall.com/lists/oss-security/2019/08/07/1
