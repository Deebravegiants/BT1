# [M] Memory Allocation with Excessive Size Value in Elasticsearch Highlighting Leading to Denial of Service

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2026-72639
Aliases: CVE-2026-72639
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2026-72639
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=9.3.0 <9.5.1

## Details
Elasticsearch does not enforce an upper bound on a user-supplied count accepted by a search highlighting option, and the allocation derived from that count is not accounted against any circuit breaker. An authenticated user holding only read privileges on a single searchable index can submit one small search request that causes the node to reserve an excessively large internal data structure. The allocation occurs before the existing highlighting safety limits are evaluated, so memory exhaustion raises a fatal error that terminates the Elasticsearch node process. This results in a denial of service for the affected node and degrades cluster routing and health. The defect is not volumetric and does not depend on the size of the indexed data, so a single request is sufficient.

## References
- https://discuss.elastic.co/t/elasticsearch-8-19-20-9-4-5-9-5-1-security-update-esa-2026-120/389503
- https://nvd.nist.gov/vuln/detail/CVE-2026-72639
