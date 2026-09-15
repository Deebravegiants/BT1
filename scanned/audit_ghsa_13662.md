# [M] Directory Traversal in jeecg-boot

## Summary
Severity: Medium
Advisory: GHSA-rgg9-264h-3hfw
CVE: CVE-2023-47467
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-22
Source: https://github.com/advisories/GHSA-rgg9-264h-3hfw
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-common` — affected >=0

## Details
Directory Traversal vulnerability in jeecg-boot v.3.6.0 allows a remote privileged attacker to obtain sensitive information via the file directory structure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47467
- https://github.com/jeecgboot/jeecg-boot-starter
- https://www.yuque.com/u2479829/tegvu8/dvmfdl5fssfen05q
