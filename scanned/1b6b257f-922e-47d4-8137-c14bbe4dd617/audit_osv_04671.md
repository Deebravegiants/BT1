# [M] Incorrect Authorization in Elasticsearch Leading to Information Disclosure

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2026-56144
Aliases: CVE-2026-56144
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2026-56144
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=9.4.0 <9.4.4

## Details
Incorrect Authorization (CWE-863) in Elasticsearch can allow an authenticated user with limited index privileges to exploit insufficient authorization controls in the ingest simulation feature. By targeting indices they are not authorized to access directly, the user can cause those indices' configured ingest pipelines to execute and return their output, potentially disclosing data processed or enriched by those pipelines. Additionally, the same feature can be used to retrieve index mapping metadata for indices the user are not authorized to access directly.

## References
- https://discuss.elastic.co/t/elasticsearch-8-19-18-9-3-7-9-4-4-security-update-esa-2026-56/388555
- https://nvd.nist.gov/vuln/detail/CVE-2026-56144
