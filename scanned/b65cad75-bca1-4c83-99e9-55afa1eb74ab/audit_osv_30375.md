# [H] RediSearch Integer Overflow with LIMIT or KNN arguments can lead to RCE

## Summary
Severity: High
Advisory: CVE-2024-51737
Aliases: GHSA-p2pg-67m3-4c76
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2024-51737
Type: osv

## Details
RediSearch is a Redis module that provides querying, secondary indexing, and full-text search for Redis. An authenticated redis user executing FT.SEARCH or FT.AGGREGATE with a specially crafted LIMIT command argument, or FT.SEARCH with a specially crafted KNN command argument, can trigger an integer overflow, leading to heap overflow and potential remote code execution. This vulnerability is fixed in 2.6.24, 2.8.21, and 2.10.10. Avoid setting value of -1 or large values for configuration parameters MAXSEARCHRESULTS and MAXAGGREGATERESULTS, to avoid exploiting large LIMIT arguments.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51737.json
- https://github.com/RediSearch/RediSearch/security/advisories/GHSA-p2pg-67m3-4c76
- https://nvd.nist.gov/vuln/detail/CVE-2024-51737
- https://github.com/RediSearch/RediSearch/commit/13a2936d921dbe5a2e3c72653e0bd7b26af3a6cb
