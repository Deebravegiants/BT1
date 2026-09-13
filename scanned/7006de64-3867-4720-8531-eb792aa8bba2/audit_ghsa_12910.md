# [M] Zip4j Origin Validation Error

## Summary
Severity: Medium
Advisory: GHSA-2pj2-gchf-wmw7
CVE: CVE-2023-22899
CWE: CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-01-10
Source: https://github.com/advisories/GHSA-2pj2-gchf-wmw7
Type: github-advisory

## Affected
- Maven: `net.lingala.zip4j:zip4j` — affected >=0 <2.11.3

## Details
Zip4j through 2.11.2, as used in Threema and other products, does not always check the MAC when decrypting a ZIP archive. This issue has been fixed in version 2.11.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22899
- https://github.com/srikanth-lingala/zip4j/issues/485
- https://breakingthe3ma.app
- https://breakingthe3ma.app/files/Threema-PST22.pdf
- https://github.com/srikanth-lingala/zip4j
- https://github.com/srikanth-lingala/zip4j/releases
- https://github.com/srikanth-lingala/zip4j/releases/tag/v2.11.3
- https://news.ycombinator.com/item?id=34316206
- https://threema.ch/en/blog/posts/news-alleged-weaknesses-statement
