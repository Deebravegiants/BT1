# [C] Dify < 1.16.0-rc1 SQL Injection via MyScale Vector Store search_by_full_text

## Summary
Severity: Critical
Advisory: CVE-2026-61461
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-61461
Type: osv

## Details
Dify before 1.16.0-rc1 contains a SQL injection vulnerability in the MyScale vector store backend that allows attackers to execute arbitrary SQL by supplying unsanitized search parameters to the search_by_full_text method without escaping or parameterization. Attackers can inject malicious SQL through the search parameters to read, modify, or delete data in the underlying ClickHouse database.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61461.json
- https://github.com/langgenius/dify/releases/tag/1.16.0-rc1
- https://nvd.nist.gov/vuln/detail/CVE-2026-61461
- https://www.vulncheck.com/advisories/dify-rc1-sql-injection-via-myscale-vector-store-search-by-full-text
- https://github.com/langgenius/dify/pull/38295
- https://github.com/langgenius/dify/commit/d9884efaeea8322706e24c560d2c17e5bf3fab5f
- https://github.com/langgenius/dify
- https://github.com/langgenius/dify/issues/38281
