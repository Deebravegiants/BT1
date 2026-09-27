# [M] Jenkins Aqua MicroScanner Plugin showed plain text credential in configuration form 

## Summary
Severity: Medium
Advisory: GHSA-vv4q-2w98-4v8g
CVE: CVE-2019-10427
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vv4q-2w98-4v8g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:aqua-microscanner` — affected >=0 <1.0.8

## Details
Jenkins Aqua MicroScanner Plugin 1.0.7 and earlier transmitted configured credentials in plain text as part of the global Jenkins configuration form, potentially resulting in their exposure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10427
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-1507
- http://www.openwall.com/lists/oss-security/2019/09/25/3
