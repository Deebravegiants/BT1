# [M] Apache Tika Denial of Service due to Infinite Loop in Tika's SQLite3Parser

## Summary
Severity: Medium
Advisory: GHSA-3448-vfvv-xp9g
CVE: CVE-2018-17197
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-12-26
Source: https://github.com/advisories/GHSA-3448-vfvv-xp9g
Type: github-advisory

## Affected
- Maven: `org.apache.tika:tika-parsers` — affected >=1.8 <1.20

## Details
A carefully crafted or corrupt sqlite file can cause an infinite loop in Apache Tika's SQLite3Parser in versions 1.8-1.19.1 of Apache Tika.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17197
- https://github.com/advisories/GHSA-3448-vfvv-xp9g
- https://lists.apache.org/thread.html/7c021a4ea2037e52e74628e17e8e0e2acab1f447160edc8be0eae6d3@%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/r204ba2a9ea750f38d789d2bb429cc0925ad6133deea7cbc3001d96b5@%3Csolr-user.lucene.apache.org%3E
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- http://www.securityfocus.com/bid/106293
