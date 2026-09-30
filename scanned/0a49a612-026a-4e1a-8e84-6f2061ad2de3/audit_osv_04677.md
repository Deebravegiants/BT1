# [M] Inefficient Algorithmic Complexity in Elasticsearch Leading to Denial of Service

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2026-72685
Aliases: CVE-2026-72685
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2026-72685
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=9.0.0 <9.4.5

## Details
A flaw in Elasticsearch allows a low-privileged authenticated user who can index documents to submit a single small document containing a crafted user-supplied input. Processing one such document occupies a worker thread from a bounded pool for a disproportionate amount of time, degrading the availability of indexing operations on the affected node.

## References
- https://discuss.elastic.co/t/elasticsearch-8-19-20-9-4-5-security-update-esa-2026-77/389500
- https://nvd.nist.gov/vuln/detail/CVE-2026-72685
