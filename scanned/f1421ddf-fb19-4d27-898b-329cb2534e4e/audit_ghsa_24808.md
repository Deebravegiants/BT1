# [M] Arbitrary file read vulnerability in Jenkins File System SCM Plugin

## Summary
Severity: Medium
Advisory: GHSA-47rr-8vrp-9283
CVE: CVE-2019-10375
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-47rr-8vrp-9283
Type: github-advisory

## Affected
- Maven: `hudson.plugins.filesystem_scm:filesystem_scm` — affected >=0

## Details
An arbitrary file read vulnerability in Jenkins File System SCM Plugin 2.1 and earlier allows attackers able to configure jobs in Jenkins to obtain the contents of any file on the Jenkins master.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10375
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-569
- http://www.openwall.com/lists/oss-security/2019/08/07/1
