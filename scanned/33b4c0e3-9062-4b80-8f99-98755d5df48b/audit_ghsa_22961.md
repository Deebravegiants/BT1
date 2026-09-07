# [M] Fortify Plugin stored credentials in plain text

## Summary
Severity: Medium
Advisory: GHSA-xr37-pjfh-qwwc
CVE: CVE-2020-2107
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xr37-pjfh-qwwc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fortify` — affected >=0 <19.2.30

## Details
Fortify Plugin 19.1.29 and earlier stored its proxy server password unencrypted in job `config.xml` files. This password could be read by users with the Extended Read permission.

Fortify Plugin 19.2.30 now encrypts the proxy server password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2107
- https://github.com/jenkinsci/fortify-plugin
- https://jenkins.io/security/advisory/2020-01-29/#SECURITY-1565
- http://www.openwall.com/lists/oss-security/2020/01/29/1
