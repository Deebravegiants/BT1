# [M] llmware 0.4.6 SQL Injection via unescaped filter values

## Summary
Severity: Medium
Advisory: CVE-2026-85689
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85689
Type: osv

## Details
llmware 0.4.6 contains an SQL injection vulnerability in the collection-database layer (llmware/resources.py) where filter and lookup values are directly string-interpolated into SQL WHERE clauses without parameterization or escaping, in both the SQLite and PostgreSQL backends. The filter validator only checks keys against an allow-list and never sanitizes values. Attacker-controlled filter values reaching the public API via Library.block_lookup and Query.text_query_with_custom_filter / text_query_by_author_or_speaker can neutralize the intended filter to disclose rows the caller was scoped out of (cross-document/cross-collection disclosure); on PostgreSQL the flaw permits boolean- and UNION-based SQL injection.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85689.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85689
- https://www.vulncheck.com/advisories/llmware-0.4.6-sql-injection-via-unescaped-filter-values
- https://github.com/llmware-ai/llmware/issues/1304
- https://github.com/llmware-ai/llmware
- https://github.com/llmware-ai/llmware/blob/v0.4.6/llmware/resources.py
