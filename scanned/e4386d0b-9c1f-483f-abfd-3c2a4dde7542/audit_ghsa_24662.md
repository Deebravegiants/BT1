# [M] Missing permission check in Jenkins Avatar Plugin

## Summary
Severity: Medium
Advisory: GHSA-mg72-h5gj-8gg7
CVE: CVE-2019-10377
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mg72-h5gj-8gg7
Type: github-advisory

## Affected
- Maven: `net.hurstfrost.jenkins:avatar` — affected >=0

## Details
A missing permission check in Jenkins Avatar Plugin 1.2 and earlier allows attackers with Overall/Read access to change the avatar of any user of Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10377
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-1099
- http://www.openwall.com/lists/oss-security/2019/08/07/1
