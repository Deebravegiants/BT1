# [M] Reachable Assertion in Elasticsearch Leading to Denial of Service

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2026-63140
Aliases: CVE-2026-63140
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2026-63140
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=9.4.0 <9.4.4

## Details
Reachable Assertion (CWE-617) in Elasticsearch can lead to denial of service via Input Data Manipulation (CAPEC-153). A specially crafted search request containing a null value in a specific query clause causes an internal assertion to be raised during query parsing. Because Elasticsearch treats assertion failures as fatal errors, this terminates the affected node process. A low-privileged authenticated user with read access to at least one index can exploit this condition with a single request to cause a node to terminate, disrupting search availability. In a single-node deployment this fully stops Elasticsearch; in a multi-node cluster it reduces cluster capacity for each affected node.

## References
- https://discuss.elastic.co/t/elasticsearch-8-19-19-9-3-8-9-4-4-security-update-esa-2026-64/388565
- https://nvd.nist.gov/vuln/detail/CVE-2026-63140
