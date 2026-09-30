# [M] Allocation of Resources Without Limits or Throttling in Elasticsearch Leading to Denial of Service

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2026-56143
Aliases: CVE-2026-56143
Ecosystem: Bitnami
Published: 2026-09-07
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2026-56143
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=9.0.0 <9.3.0

## Details
Allocation of Resources Without Limits or Throttling (CWE-770) in Elasticsearch can lead to a denial of service via Excessive Allocation (CAPEC-130). A user with elevated privileges can submit a specially crafted request that causes excessive memory consumption, which may render the affected node unavailable.

## References
- https://discuss.elastic.co/t/elasticsearch-8-19-20-9-3-0-security-update-esa-2026-47/390084
- https://nvd.nist.gov/vuln/detail/CVE-2026-56143
