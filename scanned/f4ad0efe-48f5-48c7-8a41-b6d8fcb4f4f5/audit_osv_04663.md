# [M] BIT-elasticsearch-2021-22137

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2021-22137
Aliases: CVE-2021-22137, GHSA-hr65-qq6p-87r4
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2021-22137
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=7.11.0 <7.11.2

## Details
In Elasticsearch versions before 7.11.2 and 6.8.15 a document disclosure flaw was found when Document or Field Level Security is used. Search queries do not properly preserve security permissions when executing certain cross-cluster search queries. This could result in the search disclosing the existence of documents the attacker should not be able to view. This could result in an attacker gaining additional insight into potentially sensitive indices.

## References
- https://discuss.elastic.co/t/elastic-stack-7-12-0-and-6-8-15-security-update/268125
- https://security.netapp.com/advisory/ntap-20210625-0003/
- https://nvd.nist.gov/vuln/detail/CVE-2021-22137
