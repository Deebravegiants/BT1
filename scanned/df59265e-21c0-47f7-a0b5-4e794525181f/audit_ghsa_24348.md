# [M] Improper Limitation of a Pathname to a Restricted Directory in Zip4j

## Summary
Severity: Medium
Advisory: GHSA-2rpm-4x8c-pvqg
CVE: CVE-2018-1002202
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-2rpm-4x8c-pvqg
Type: github-advisory

## Affected
- Maven: `net.lingala.zip4j:zip4j` — affected >=0 <1.3.3

## Details
zip4j before 1.3.3 is vulnerable to directory traversal, allowing attackers to write to arbitrary files via a ../ (dot dot slash) in a Zip archive entry that is mishandled during extraction. This vulnerability is also known as 'Zip-Slip'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1002202
- https://github.com/snyk/zip-slip-vulnerability
- https://snyk.io/research/zip-slip-vulnerability
- https://snyk.io/vuln/SNYK-JAVA-NETLINGALAZIP4J-31679
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbmu03895en_us
