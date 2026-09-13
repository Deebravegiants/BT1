# [M] EC-CUBE vulnerable to authorization bypass

## Summary
Severity: Medium
Advisory: GHSA-j2hg-w4p4-6rvm
CVE: CVE-2014-0808
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j2hg-w4p4-6rvm
Type: github-advisory

## Affected
- Packagist: `ec-cube/ec-cube` — affected >=2.11.0 <2.12.2

## Details
Authorization bypass through user-controlled key issue exists in EC-CUBE 2.11.0 through 2.12.2 and EC-Orange systems deployed before June 29th, 2015. If this vulnerability is exploited, a user of the affected shopping website may obtain other users' information by sending a crafted HTTP request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0808
- https://github.com/EC-CUBE/ec-cube
- https://jvn.jp/en/jp/JVN15637138
- https://jvndb.jvn.jp/jvndb/JVNDB-2024-000054
- http://jvn.jp/en/jp/JVN51770585
- http://jvn.jp/en/jp/JVN51770585/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2014-000006
- http://www.ec-cube.net/info/weakness/weakness.php?id=57
