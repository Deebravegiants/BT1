# [M] BIT-elasticsearch-2020-7021

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2020-7021
Aliases: CVE-2020-7021, GHSA-cqgv-256r-m9r8
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2020-7021
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=7.0.0 <7.10.0

## Details
Elasticsearch versions before 7.10.0 and 6.8.14 have an information disclosure issue when audit logging and the emit_request_body option is enabled. The Elasticsearch audit log could contain sensitive information such as password hashes or authentication tokens. This could allow an Elasticsearch administrator to view these details.

## References
- https://discuss.elastic.co/t/elastic-stack-7-11-0-and-6-8-14-security-update/263915
- https://security.netapp.com/advisory/ntap-20210319-0003/
- https://nvd.nist.gov/vuln/detail/CVE-2020-7021
