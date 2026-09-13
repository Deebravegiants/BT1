# [H] pgvector buffer overflow in parallel HNSW index build

## Summary
Severity: High
Advisory: CVE-2026-3172
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-3172
Type: osv

## Details
Buffer overflow in parallel HNSW index build in pgvector 0.6.0 through 0.8.1 allows a database user to leak sensitive data from other relations or crash the database server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3172.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3172
- https://github.com/pgvector/pgvector/issues/959
