# [M] BIT-elasticsearch-2021-22134

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2021-22134
Aliases: CVE-2021-22134, GHSA-hwvv-438r-mhvj
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2021-22134
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=7.6.0 <7.11.1

## Details
A document disclosure flaw was found in Elasticsearch versions after 7.6.0 and before 7.11.0 when Document or Field Level Security is used. Get requests do not properly apply security permissions when executing a query against a recently updated document. This affects documents that have been updated and not yet refreshed in the index. This could result in the search disclosing the existence of documents and fields the attacker should not be able to view.

## References
- https://discuss.elastic.co/t/elastic-stack-7-11-0-security-update/265835
- https://security.netapp.com/advisory/ntap-20210430-0006/
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-22134
