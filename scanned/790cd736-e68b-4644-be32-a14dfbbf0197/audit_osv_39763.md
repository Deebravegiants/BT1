# [M] Improper Search Cache Isolation for Scoped Search API Keys in Typesense

## Summary
Severity: Medium
Advisory: CVE-2026-47225
Aliases: GHSA-97x4-gm45-jpcw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-47225
Type: osv

## Details
Typesense is a fast, typo-tolerant search engine. Prior to versions 29.1 and 30.2, there is a cache isolation issue affecting search requests that use both server-side search result caching and Scoped Search API Keys. Under specific request ordering, cached search results could be reused across requests with different Scoped Search API Key constraints. This could result in a request receiving search results that should have been restricted by its Scoped Search API Key. This issue only affects search requests that use both server-side search result caching and Scoped Search API Keys with embedded filters to restrict access to search results within a collection. This vulnerability may result in unintended disclosure of search results across scoped authorization contexts. This issue has been patched in versions 29.1 and 30.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47225.json
- https://github.com/typesense/typesense/security/advisories/GHSA-97x4-gm45-jpcw
- https://nvd.nist.gov/vuln/detail/CVE-2026-47225
