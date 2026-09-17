# [M] CVE-2023-22847

## Summary
Severity: Medium
Advisory: CVE-2023-22847
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-03-07
Source: https://osv.dev/vulnerability/CVE-2023-22847
Type: osv

## Details
Information disclosure vulnerability exists in pg_ivm versions prior to 1.5.1. An Incrementally Maintainable Materialized View (IMMV) created by pg_ivm may reflect rows with Row-Level Security that the owner of the IMMV should not have access to. As a result, information in tables protected by Row-Level Security may be retrieved by a user who is not authorized to access it.

## References
- https://github.com/sraoss/pg_ivm/releases/tag/v1.5.1
- https://jvn.jp/en/jp/JVN19872280/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22847.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-22847
- https://github.com/sraoss/pg_ivm
