# [M] Authorization Bypass via Client-Supplied $search.mergingPipeline Leaks Unauthorized Collection Data Through $$SEARCH_META

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-13057
Aliases: CVE-2026-13057
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13057
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
An issue in the server’s Atlas Search integration allows an authenticated user to bypass per-user access controls.



In sharded topologies, the $search and $searchMeta aggregation stages use internal routing that is normally populated only by the trusted router during sharded search planning. Due to insufficient input validation, an authenticated client can supply these fields directly.

## References
- https://jira.mongodb.org/browse/SERVER-126247
- https://nvd.nist.gov/vuln/detail/CVE-2026-13057
