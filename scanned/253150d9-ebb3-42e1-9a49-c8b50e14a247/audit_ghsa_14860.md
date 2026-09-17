# [M] PingCAP TiDB nil pointer dereference

## Summary
Severity: Medium
Advisory: GHSA-9g6g-xqv5-8g5w
CVE: CVE-2024-37820
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-06-25
Source: https://github.com/advisories/GHSA-9g6g-xqv5-8g5w
Type: github-advisory

## Affected
- Go: `github.com/pingcap/tidb` — affected >=0 <8.2.0

## Details
A nil pointer dereference in PingCAP TiDB v8.2.0-alpha-216-gfe5858b allows attackers to crash the application via expression.inferCollation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37820
- https://github.com/pingcap/tidb/issues/53580
- https://github.com/pingcap/tidb/commit/3d68bd21240c610c6307713e2bd54a5e71c32608
- https://gist.github.com/ycybfhb/a9c1e14ce281f2f553adca84d384b761
- https://github.com/advisories/GHSA-9g6g-xqv5-8g5w
- https://github.com/pingcap/tidb
