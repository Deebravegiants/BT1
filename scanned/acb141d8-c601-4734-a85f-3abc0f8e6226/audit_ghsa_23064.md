# [M] Improper Limitation of a Pathname to a Restricted Directory in zt-zip

## Summary
Severity: Medium
Advisory: GHSA-qcf3-9vmh-xw4r
CVE: CVE-2018-1002201
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qcf3-9vmh-xw4r
Type: github-advisory

## Affected
- Maven: `org.zeroturnaround:zt-zip` — affected >=0 <1.13

## Details
zt-zip before 1.13 is vulnerable to directory traversal, allowing attackers to write to arbitrary files via a ../ (dot dot slash) in a Zip archive entry that is mishandled during extraction. This vulnerability is also known as 'Zip-Slip'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1002201
- https://github.com/zeroturnaround/zt-zip/commit/759b72f33bc8f4d69f84f09fcb7f010ad45d6fff
- https://github.com/snyk/zip-slip-vulnerability
- https://github.com/zeroturnaround/zt-zip/blob/zt-zip-1.13/Changelog.txt
- https://snyk.io/research/zip-slip-vulnerability
- https://snyk.io/vuln/SNYK-JAVA-ORGZEROTURNAROUND-31681
