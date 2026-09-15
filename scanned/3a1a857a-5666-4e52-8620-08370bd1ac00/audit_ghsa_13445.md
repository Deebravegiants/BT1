# [M] Apache Zeppelin Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gm67-h5wr-w3cv
CVE: CVE-2021-28655
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-gm67-h5wr-w3cv
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin` — affected >=0 <0.10.0

## Details
The improper Input Validation vulnerability in `Move folder to Trash` feature of Apache Zeppelin allows an attacker to delete the arbitrary files. This issue affects Apache Zeppelin Apache Zeppelin version 0.9.0 and prior versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28655
- https://github.com/apache/zeppelin
- https://lists.apache.org/thread/bxs056g3xlsofz0jb3wny9dw4llwptd2
