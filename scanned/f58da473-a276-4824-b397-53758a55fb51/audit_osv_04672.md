# [M] Uncontrolled Recursion in Elasticsearch Leading to Denial of Service

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2026-56148
Aliases: CVE-2026-56148
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2026-56148
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=9.4.0 <9.4.3

## Details
Uncontrolled Recursion (CWE-674) in Elasticsearch can lead to a denial of service via Excessive Allocation (CAPEC-130). An authenticated user can submit a specially crafted query that causes excessive resource consumption while the request is processed, which may render the affected node unavailable.

## References
- https://discuss.elastic.co/t/elasticsearch-8-19-17-9-3-6-9-4-3-security-update-esa-2026-42
- https://nvd.nist.gov/vuln/detail/CVE-2026-56148
