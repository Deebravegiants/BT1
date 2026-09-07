# [M] hawtio vulnerable to Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-p223-c4w6-q454
CVE: CVE-2023-33544
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-06-01
Source: https://github.com/advisories/GHSA-p223-c4w6-q454
Type: github-advisory

## Affected
- Maven: `io.hawt:project` — affected >=0

## Details
hawtio 2.17.2 is vulnerable to Path Traversal. it is possible to input malicious zip files, which can result in the high-risk files after decompression being stored in any location, even leading to file overwrite.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33544
- https://github.com/hawtio/hawtio/issues/2832
- https://github.com/hawtio/hawtio
