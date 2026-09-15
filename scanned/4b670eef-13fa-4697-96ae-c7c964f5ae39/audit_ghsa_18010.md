# [H] NodeBB SQL Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-rfh2-8vxq-jqr8
CVE: CVE-2025-50979
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-27
Source: https://github.com/advisories/GHSA-rfh2-8vxq-jqr8
Type: github-advisory

## Affected
- npm: `nodebb` — affected >=0

## Details
NodeBB v4.3.0 is vulnerable to SQL injection in its search-categories API endpoint (/api/v3/search/categories). The search query parameter is not properly sanitized, allowing unauthenticated, remote attackers to inject boolean-based blind and PostgreSQL error-based payloads.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-50979
- https://github.com/4rdr/proofs/blob/main/info/NodeBB-v4.3.0.-SQL-Injection-via-search-parameter.md
- https://github.com/NodeBB/NodeBB
