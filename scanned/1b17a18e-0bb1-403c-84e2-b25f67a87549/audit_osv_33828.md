# [H] CVE-2025-50983

## Summary
Severity: High
Advisory: CVE-2025-50983
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2025-08-27
Source: https://osv.dev/vulnerability/CVE-2025-50983
Type: osv

## Details
SQL Injection vulnerability exists in the sortKey parameter of the GET /api/v1/wanted/cutoff API endpoint in readarr 0.4.15.2787. The endpoint fails to properly sanitize user-supplied input, allowing attackers to inject and execute arbitrary SQL commands against the backend SQLite database. Sqlmap confirmed exploitation via stacked queries, demonstrating that the parameter can be abused to run arbitrary SQL statements. A heavy query was executed using SQLite's RANDOMBLOB() and HEX() functions to simulate a time-based payload, indicating deep control over database interactions.

## References
- https://github.com/4rdr/proofs/blob/main/info/readarr-0.4.15.2787-sql-injection-via-sortkey-parameter.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50983.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50983
