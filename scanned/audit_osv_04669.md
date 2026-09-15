# [M] Uncontrolled Resource Consumption in Elasticsearch Leading to Denial of Service

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2026-49090
Aliases: CVE-2026-49090
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2026-49090
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=8.0.0 <8.15.0

## Details
Uncontrolled Resource Consumption (CWE-400) in Elasticsearch can lead to a denial of service via Excessive Allocation (CAPEC-130). An authenticated user can submit a specially crafted bulk request that causes sustained high CPU consumption, which can render the affected node unable to process requests.

## References
- https://discuss.elastic.co/t/elasticsearch-7-17-24-8-15-0-security-update-esa-2026-52
- https://nvd.nist.gov/vuln/detail/CVE-2026-49090
